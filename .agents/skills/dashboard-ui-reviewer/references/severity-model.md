# Severity model

## Critical

Broken, unusable, or misleading: runtime failure, broken navigation, misleading data display, inaccessible essential control, or severe layout corruption.

## High

Significantly harms comprehension or task completion: absent primary hierarchy, buried important metric, unreadable major chart, severe overflow, or ambiguous primary interaction.

## Medium

Meaningfully reduces usability, analytical clarity, or polish: inconsistent spacing, weak labels, redundant visualization, or inconsistent component treatment.

## Low

Minor refinement.

Never spend an iteration primarily fixing Low findings while Critical or High findings remain. A shared issue appearing on two or more pages is a root-cause candidate and should be investigated in shared components, tokens, CSS, chart factories, or layout helpers.

