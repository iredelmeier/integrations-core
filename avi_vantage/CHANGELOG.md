# CHANGELOG - Avi Vantage

## 3.1.1 / 2022-05-18 / Agent 7.37.0

* [Fixed] Fix extra metrics description example. See [#12043](https://github.com/DataDog/integrations-core/pull/12043).

## 3.1.0 / 2022-04-05 / Agent 7.36.0

* [Added] Add metric_patterns options to filter all metric submission by a list of regexes. See [#11695](https://github.com/DataDog/integrations-core/pull/11695).
* [Fixed] Remove outdated warning in the description for the `tls_ignore_warning` option. See [#11591](https://github.com/DataDog/integrations-core/pull/11591).

## 3.0.0 / 2022-02-19 / Agent 7.35.0

* [Added] Add `pyproject.toml` file. See [#11317](https://github.com/DataDog/integrations-core/pull/11317).
* [Fixed] Fix namespace packaging on Python 2. See [#11532](https://github.com/DataDog/integrations-core/pull/11532).
* [Changed] Add tls_protocols_allowed option documentation. See [#11251](https://github.com/DataDog/integrations-core/pull/11251).

## 2.1.1 / 2022-01-08 / Agent 7.34.0

* [Fixed] Add comment to autogenerated model files. See [#10945](https://github.com/DataDog/integrations-core/pull/10945).

## 2.1.0 / 2021-11-13 / Agent 7.33.0

* [Added] Document new include_labels option. See [#10617](https://github.com/DataDog/integrations-core/pull/10617).
* [Added] Document new use_process_start_time option. See [#10601](https://github.com/DataDog/integrations-core/pull/10601).

## 2.0.3 / 2021-10-15 / Agent 7.32.0

* [Fixed] [OpenMetricsV2] Allow empty namespaces. See [#10420](https://github.com/DataDog/integrations-core/pull/10420).

## 2.0.2 / 2021-10-12

* [Fixed] Bump base package requirements. See [#10390](https://github.com/DataDog/integrations-core/pull/10390).

## 2.0.1 / 2021-10-05

* [Fixed] Remove `server` from the list of generic tags. See [#10344](https://github.com/DataDog/integrations-core/pull/10344).

## 2.0.0 / 2021-10-04

* [Added] Add HTTP option to control the size of streaming responses. See [#10183](https://github.com/DataDog/integrations-core/pull/10183).
* [Added] Add allow_redirect option. See [#10160](https://github.com/DataDog/integrations-core/pull/10160).
* [Added] Disable generic tags. See [#10027](https://github.com/DataDog/integrations-core/pull/10027).
* [Fixed] Fix the description of the `allow_redirects` HTTP option. See [#10195](https://github.com/DataDog/integrations-core/pull/10195).
* [Fixed] Add server as generic tag. See [#10100](https://github.com/DataDog/integrations-core/pull/10100).
* [Changed] Add disable_generic tag. See [#10164](https://github.com/DataDog/integrations-core/pull/10164).

## 1.0.1 / 2021-08-23 / Agent 7.31.0

* [Fixed] Bump base package requirement. See [#9960](https://github.com/DataDog/integrations-core/pull/9960).

## 1.0.0 / 2021-08-06

* [Added] Add Avi Vantage integration. See [#9481](https://github.com/DataDog/integrations-core/pull/9481).
