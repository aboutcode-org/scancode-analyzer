Selecting Incorrect Scan Cases
==============================

Dividing Matches into Region Groups
-----------------------------------

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


Only Selecting Files with Incorrect Scans
-----------------------------------------

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
