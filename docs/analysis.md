# Analysis of Flipper Ruby Gem

## Overview

Flipper is a Ruby feature‑flagging library that lets developers enable or disable features for specific users, groups, time windows or percentages of actors.  The core gem provides the feature‑flag DSL (domain specific language), types and gate logic, while separate adapter gems (e.g., flipper‑active_record) persist flag data in different stores (ActiveRecord, Redis, etc.).  For Ruby on Rails applications, Flipper Cloud offers a hosted UI and multi‑environment synchronization but the open‑source library can be used independently.

At a high level, Flipper exposes a Flipper module which returns a DSL instance configured with a storage adapter.  The DSL acts as the main API for creating and managing feature flags.  Each feature has one or more gates that specify whether the feature is enabled based on boolean state, actors, groups, percentage of actors, percentage of time or expressions.  Flipper supports instrumentation, memoization and read‑only adapters.

## Core classes and architecture

### The Flipper module

The entry point is Flipper.new(adapter, options), which returns a DSL configured with the provided storage adapter ￼.  The module provides convenience methods that delegate to the per‑thread DSL instance, e.g. Flipper.enabled?(:search, current_user), Flipper.enable(:search), and Flipper.disable(:search).  It also exposes helper methods to construct boolean/number/string/actor/group expressions and a registry for custom groups ￼.

### DSL (Flipper::DSL)

The DSL encapsulates a storage adapter and exposes a fluent API for working with features.  It accepts an adapter and options (instrumenter and memoization) on initialization ￼.  Its key methods include:
* enabled? – checks if a feature is enabled for one or more actors ￼.
* enable / disable – enable or disable a feature (optionally for actors, groups, or percentages) ￼ ￼.
* enable_actor, enable_group, enable_percentage_of_time and enable_percentage_of_actors – convenience methods to enable a feature for specific actors, groups or percentages ￼.
* disable_actor, disable_group, disable_percentage_of_time, disable_percentage_of_actors – disable the feature for specific scopes ￼.
* add, exist?, remove, clear – manage the feature’s presence in storage and clear gate values.

### Feature (Flipper::Feature)

A Feature instance wraps a feature name and adapter.  When enable or disable is called, the feature asks the adapter to add itself to the features table and then enables/disables the appropriate gate ￼.  Feature#enabled? constructs a FeatureCheckContext containing the feature’s current gate values and given actors, then checks whether any gate is open ￼.  The class also provides helper methods like enable_actor, enable_group, enable_percentage_of_time, enable_percentage_of_actors, enable_expression and their disable counterparts ￼.

### Gates (Flipper::Gate and subclasses)

A gate encapsulates a rule that determines whether a feature is enabled for a given context.  The abstract Flipper::Gate defines the API (e.g., name, key, data_type, enabled?, open?, wrap) ￼.  Flipper ships with several gate types:
* Boolean gate – stores a boolean value; open if the stored value is true ￼.  It wraps input into a boolean type and treats true/false values as the only actors it protects ￼.
* Actor gate – enabled for individual actors (objects that respond to flipper_id).  Actors are wrapped into Flipper::Types::Actor which uses the actor’s flipper_id as the persistent value ￼.
* Group gate – enabled for groups (named sets of actors defined by a block).  A Group holds a symbol name and an optional matching block; when evaluating, the block receives the actor and feature context and should return true when the actor belongs to the group ￼.
* Percentage gates – PercentageOfActors and PercentageOfTime.  These wrap numbers between 0 and 100 and use the actor’s ID or wall‑clock time to produce a deterministic hash used to decide if the actor falls into the enabled percentage ￼.  A PercentageOfActors gate extends Percentage with no additional logic ￼.
* Expression gate – stores complex logical expressions (e.g., any/all, property comparisons) in JSON.

During a feature check, gates are evaluated in a defined order: expression, boolean, group, actor, percentage of actors and percentage of time.  The first gate that returns true means the feature is enabled ￼.

### Types (Flipper::Types)

Flipper wraps various values into type objects to standardize persistence and comparison.  The base class Type stores a value and defines equality based on class and value ￼.  Types::Actor wraps an actor and uses its flipper_id as the persisted value ￼.  Types::Group stores a group name and optional matching block ￼.  Types::Percentage validates that the value is between 0 and 100 ￼.  Wrapping ensures that adapters always receive consistent string representations for keys and values.

### Adapter interface and built‑in adapters

An adapter provides persistence for features and gates.  It includes the Flipper::Adapter module, which defines API methods such as features, add, remove, clear, get, get_multi, enable, disable, import and export ￼.  The default adapter for the gem is an in‑memory store (Adapters::Memory), but there are official adapters for Redis, Memcached (Dalli), Mongo, Sequel, and ActiveRecord.

The ActiveRecord adapter persists feature flags in a relational database.  On initialization it accepts optional parameters for a custom name, feature model and gate model ￼.  The adapter’s key methods operate within database transactions:
* features returns the set of feature keys from the flipper_features table ￼.
* add inserts a row into the features table if it does not already exist ￼.
* remove deletes the feature row and all associated gate rows ￼.
* clear removes all gate rows for a feature ￼.
* get returns gate values for a feature by querying the gates table ￼.
* get_multi fetches gate values for multiple features in a single query ￼.
* get_all performs a join between features and gates tables and groups the results ￼.
* enable/disable call set, enable_multi, delete or clear depending on the gate’s data type ￼.  Booleans clear existing values before setting a new value; set gates append values; JSON gates store JSON using Typecast.to_json ￼ ￼.

### ActiveRecord models and database schema

The ActiveRecord adapter defines two internal models:
* Feature model – inherits from Flipper::Adapters::ActiveRecord::Model (an abstract ActiveRecord::Base) and maps to the flipper_features table ￼.  It has one‑to‑many association has_many :gates on feature_key and validates presence of key ￼.
* Gate model – also inherits from the base model and maps to the flipper_gates table ￼.  It validates presence of feature_key and key.

When developers run rails generate flipper:setup (or flipper:active_record), Flipper provides a migration template that creates the necessary tables and indexes.  The migration defines flipper_features with a string key and timestamps and flipper_gates with feature_key, key, value (text) and timestamps.  It adds a unique index on flipper_features.key and a unique composite index on flipper_gates.feature_key, key and value ￼.  The index on value is restricted to 255 characters for MySQL compatibility ￼.  On rollback the migration drops both tables ￼.


### Schema summary

|Table|Columns (type, constraints)|Purpose|
|flipper_features|id (PK), key (string, not null), created_at, updated_at. Unique index on key .|Stores one row per feature.|
|flipper_gates|id (PK), feature_key (string, not null), key (string, not null), value (text), created_at, updated_at. Unique index on (feature_key, key, value) .|Stores values for each gate of a feature; one row per boolean state, group, actor or percentage.|

A Feature row is added when a feature is enabled or disabled for the first time.  A Gate row stores the specific gating rule.  For example, enabling a feature globally inserts a row where key='boolean' and value='true'; enabling for a group inserts a row with key='groups' and value equal to the group name.  Because the index on feature_key, key and value is unique, each actor, group or percentage can only appear once per feature, and a boolean gate can only have one value.

Other adapters

Flipper includes adapters for Redis, Dalli (Memcached), Mongo, Sequel and memory.  All adapters implement the same API as described above.  For example, the Redis adapter stores feature keys and gate sets in Redis hashes/sets; the Mongo and Sequel adapters create similar flipper_features and flipper_gates collections or tables; the memory adapter uses Ruby hashes for fast in‑memory operations.  The gem also provides wrappers like Strict (raises if unknown features or gates are used), Instrumented (emits notifications on operations) and Memoizable (memoizes adapter reads within a thread).

Key design patterns
  1. Adapter pattern – Flipper decouples feature‑flag logic from storage.  The Adapter interface ensures that different persistence layers implement the same methods, allowing developers to swap adapters without changing application code.
  2. Composition via gates – Each feature holds a list of gates.  The gates are evaluated in order, and the first gate that is open returns true.  This makes the system extensible; new gate types can be added by subclassing Flipper::Gate.
  3. Type wrapping and value casting – Using wrapper types (Actor, Group, Percentage, Boolean) ensures a consistent interface for adapters and simplifies persistence (e.g., storing actor.flipper_id rather than the object itself).  Flipper::Typecast converts between Ruby objects and stored values (e.g., JSON for expressions).
  4. Memoization and instrumentation – The DSL optionally wraps the adapter with a memoizable adapter to cache reads within a request ￼.  It also accepts an instrumenter (e.g., ActiveSupport::Notifications) to emit instrumentation events for operations.
  5. Thread‑local configuration – Flipper stores the default DSL instance per thread (e.g., Thread.current[:flipper_instance]) ￼.  This allows safe concurrent use in multi‑threaded environments.

Considerations when porting to Python

Implementing a similar package in Python would involve translating these concepts:
  1. DSL / API – Provide a simple API such as flipper.is_enabled("search", actor), flipper.enable("search"), flipper.enable_for_group("search", "admins") and so on.  Consider implementing both a module‑level convenience API and an explicit instance class for configuration (similar to Flipper.new(adapter)).
  2. Feature and gate objects – Represent each feature as an object with a name and a list of gates.  Gates should be separate classes with methods name, key, data_type, is_open(context) and wrap(thing).  Evaluate gates in a fixed order (expression → boolean → group → actor → percentage of actors → percentage of time).
  3. Types / wrappers – Create wrapper classes for actors (using actor.flipper_id or a similar method/property), groups (with a group name and matching function), percentages, booleans, numbers and custom expressions.  Wrappers should store a canonical string or numeric value for persistence.
  4. Adapters – Define an abstract adapter interface with methods features(), add(feature), remove(feature), clear(feature), get(feature), get_multi(features), enable(feature, gate, thing), disable(feature, gate, thing) and optionally import/export.  Provide concrete adapters for in‑memory storage (e.g., a dictionary), SQLAlchemy (relational databases), Redis, etc.  For a relational adapter, replicate the two‑table schema from Flipper: a flipper_features table with a unique key and timestamps, and a flipper_gates table with feature_key, key, value and timestamps.  Create appropriate indexes to enforce uniqueness on feature_key, key, value.
  5. Configuration – Allow configuring a default adapter and instrumenter, as well as per‑thread or per‑request caching.  Use Python thread‑local storage (e.g., threading.local()) to store the default flipper instance per thread.
  6. Extensibility – Design the system so that new gate types or adapters can be added without modifying existing code.  Use subclassing or composition to implement new gates; use plug‑in patterns or entry points for adapters.
  7. Testing and concurrency – Provide tests for concurrency scenarios (race conditions when adding/removing features) similar to Flipper’s usage of transactions and ActiveRecord::RecordNotUnique handling ￼ ￼.  In Python, you may need to handle IntegrityError exceptions when inserting duplicate rows.

Summary

Flipper’s architecture is built around features, gates, types and adapters.  Features represent high‑level flags; gates encode the rules for enabling a feature (boolean, actor, group, percentage, expression); types wrap input values to provide a consistent interface; and adapters persist gate data in various stores.  The ActiveRecord adapter uses two tables (flipper_features and flipper_gates) with appropriate indexes to store features and their gate values ￼.  Porting Flipper to Python would involve adopting similar patterns: a clear separation of feature logic from persistence, pluggable adapters, and deterministic evaluation of gates.  This design makes Flipper easy to use while being flexible enough to integrate with different storage backends and application frameworks.
