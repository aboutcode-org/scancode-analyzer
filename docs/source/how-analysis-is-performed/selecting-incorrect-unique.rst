Selecting Incorrect Scan Cases
==============================

The steps of analysing license matches in a file and flagging potential license detection issues
are:

1. Dividing Matches in file-regions - :ref:`location_region_number`
2. Detecting License Detection Issues in file-regions - :ref:`license_scan_analysis_result`
3. Grouping the issues into classes and subclasses of issues - :ref:`dividing_into_more_cases`
4. Getting rid of same issues across package - :ref:`ignoring_same_cases_in_package`
5. Resolving issues based on groups - :ref:`resolving_issues`

.. _location_region_number:

Dividing Matches into Region Groups
-----------------------------------

The attribute ``location_region_number`` in the analysis results has information on which
file-region the match is in.

.. note::

    The values of ``location_region_number`` are positive integers starting from 1.

.. _file_region:

File Region
^^^^^^^^^^^

A file-region is::

    A location in a file having one or multiple group of license matches, overlapping each other or
    located very closely, such that it seems to belong to one form of license declaration.
    File -> file-region is a one to many relationship.

Why we need to divide matches in a file into file-regions:

1. A file could have multiple different license information/declarations in multiple regions, and
   so issues in detecting one of these doesn't effect detection of the others.

2. If there are multiple matches in a region, they need to be analyzed as a whole, as even if most
   matches have perfect ``score`` and ``match_coverage``, only one of them with a imperfect
   `match_coverage`` would mean there is a issue with that whole file-region. For example one
   license notice can be matched to a notice rule with imperfect scores, and several small
   license reference rules.

3. In times of creating a Rule out of the issue/ dealing with it, we need the matches grouped by
   file-regions.

File-Region Example
^^^^^^^^^^^^^^^^^^^

In example - `scancode-toolkit#1907 <https://github.com/nexB/scancode-toolkit/issues/1907#issuecomment-597773239>`_

- the first GPL detection is for this line range - {"start_line": 8, "end_line": 19}
- the second is for the free-unknown for this line range: {"start_line": 349, "end_line": 350}

Now, for a single file, we group all the detections by locations, to select the ones which
are correctly detected, and the wrong detections.

Here we’re using a threshold, which is after grouping all these detections by start and end line
numbers, if two of these groups are there spaces by at least N number of lines, they will be
treated as separate groups.

Scancode also uses a similar threshold while breaking down queries into slices based on the number
of lines between them, so as the use cases are exactly similar, so we are using the same threshold.

From ``scancode/src/licensedcode/query.py``, in ``__init__`` for ``Class Query``,
``line_threshold`` is set as 4.

“Break query in runs when there are at least `line_threshold` empty lines or junk-only lines.”

File-Region Grouping Algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Algorithm as for Grouping based on Location -

- Step 1: Start from the first match, and set it's start/end line as the group boundary.
- Step 2: Go by every match executing these instructions :-
    - If entirely inside the boundary, drop.
    - If partly inside the boundary, extend boundaries to include this and then drop.
    - If very close to boundary, i.e. less than a threshold, extend boundaries to include.
    - Else, if outside boundary, go to step 1 making this match as a new group.
- Repeat until there’s no groups left.

As there’s never too many detections in a file, and there’s almost always detections which have
almost all of the matched texts, and as the matches are sorted according to their start/end lines,
this is efficient enough, and passes through the list of matches once.

.. _license_scan_analysis_result:

Only Selecting Files with Incorrect Scans
-----------------------------------------

The attribute ``license_scan_analysis_result`` in the analysis results has information on if the
file-region has any license detection issue in it, bases on coverage values, presence of extra words
or false positive tags.

.. note::

    The 5 possible values of ``license_scan_analysis_result`` are:

    1. ``correct-license-detection``
    2. ``imperfect_match_coverage``
    3. ``near_perfect_match_coverage``
    4. ``extra_words``
    5. ``false_positives``

Scancode detects most licenses accurately, so our focus is only on the parts where the detection is
poor, and so primarily in the first step we separate this from the Correct Scans.

Initially from the `matcher` information we can say that
IF the license matcher is “1-hash” or “4-spdx-id” they are correct matches, all incorrect matches
lie in the other two matchers, i.e. “2-aho” and “3-seq”.

So in ``Step 1``::

    So mark all license matches with matcher “1-hash” and “4-spdx-id” first, as none of them
    are wrong detections, and also detections where all the matches have a perfect
    ``match_coverage``, i.e. 100.

These fall into the first category::

    1. ``correct-license-detection``

Then in ``Step 2`` we come into “score” and “match_coverage” values.

There are multiple matches in a File, and the individual (for each match) scores are calculated as
``score = matched_coverage * rule_relevance``

So if the score is less, there’s two possibilities::

    i. one is that the license information present itself is inadequate, but scancode detects that
       correctly, here match_coverage is always 100.
    ii. It doesn't match entirely, making the match_coverage less than 100.

So for now, we segregate incorrect matches as follows::

    IN A FILE, among all the multiple matches per file, if even one of them has a match_coverage
    value below a threshold, (say 100), it has a wrong detection potentially, and we flag all the
    detected matches of that file, for further analysis and segregation.

There is also another case where ``score != matched_coverage * rule_relevance``, where there are
some extra words, i.e. the entire rule was matched, but there were some extra words which caused the
decrease in score.

So the 3 category of errors as classified in this step are::

    2. ``imperfect_match_coverage``
    3. ``near_perfect_match_coverage``
    4. ``extra_words``

Also note that this order is important, as if any one of the matches has this case, the entire file
will be flagged as such.

And another case taking into account the false-positives, which would be single-match, i.e.
entire file will not be flagged in the same error. This is the ``Step 3`` and here a
NLP sentence Classifier could be used to improve accuracy. The error class is called::

    5. ``false_positives``

.. _dividing_into_more_cases:

Dividing the issues into more cases
-----------------------------------

These cases (group of matches in file-regions) are then divided into more types of issues in two
steps:

- Case of License Information (Text/Notice/Tag/References)
- Sub-cases for each of these 4 cases

Go to :ref:`lic_detection_issue_types` for detailed discussions and a comprehensive list of
all possible attribute values (i.e. all types of potential license detection issue) in results.

.. _ignoring_same_cases_in_package:

Ignoring Same Incorrect Scans, Package Wise
-------------------------------------------

So in Scancode, most of the code files have the same header license notice, and some of them, which
are derived from other packages, have other different license notices.

Now this practice is common across a lot of packages, as license notices/referances/tags, or in
some cases even entire texts(I’ve not encountered examples of these?) being present in a lot of
files. Now naturally if one of these is not detected correctly by scancode license detection,
other exactly similar ones will also be not detected correctly.

We need not have all of these incorrect matches, we only need one of every unique case.

So in order to select only unique ones, we use a combination of “matched_rule_identifier”
and “match_coverage” to determine uniqueness of the matches. But we use this file-wise.

I.e. the policy is::

    If multiple files have the same N number of matches, all these matches having same
    “matched_rule_identifier” and “match_coverage” across these multiple files, we keep only
    one file among them and discard the others.

For example, in `scancode-toolkit#1920 <https://github.com/nexB/scancode-toolkit/issues/1920>`_, socat-2.0.0 has
multiple (6) files with each file having the same 3 matched rules and match_coverage sets, i.e. -

- {"gpl-3.0-plus_with_tex-exception_4.RULE", 13.21}
- {gpl-3.0-plus_with_tex-exception_4.RULE”, 13.21}
- {gpl-2.0_756.RULE", 100.0}

So, we need to keep only one of these files, as the others have the same license detection errors.

.. note::

    This isn't followed in the ``scancode`` ``post-scan plugin`` as the processing is per-file,
    and this is a codebase-level operation.
