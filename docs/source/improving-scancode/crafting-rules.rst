.. _resolving_issues:

Crafting Rules From Fragments of Matched Text
=============================================

.. note::

    The rule/.yml file generation/other actions is Work In Progress.
    Only reports with suggested rules with the rule text, license key, rule type is generated.

The functions from stitching are implemented using the same algorithm mentioned above in Deleting
Correct scans Location wise in File, because this is also done location wise, and wrt start and
end line numbers. But the other rule/.yml generation is remaining according to different treatments
for different classes of errors.

.. _crafting_rule_text:

Matched Text
------------

When two matched texts having a common boundary and has a common substring, Like in this example:-

- start_line - 16
- end_line - 17
- matched_text::

    * You should have received a copy of the GNU Lesser General Public\n * License along with this library; if not, write to the Free Software

- start_line - 17
- end_line - 19
- matched_text::

    * License along with this library; if not, write to the Free Software\n * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,\n * MA 02110-1301 USA

Here, ``License along with this library; if not, write to the Free Software`` is a substring of both
matched_texts, so we cannot simply join them, we have to join them without this repetition.

If they do have a common boundary but do not have common substrings, then they are joined simply.

Now if they do not have a common boundary,

- Less than or equal to 4 lines gap: They are joined as one Rule
- More than 4 lines gap: They are made two separate rules

.. _crafting_rule_yml:

``.yml`` file attributes
------------------------

1. The boolean value denoting the license type, i.e. license text/notice/tag/reference is determined
   from their respective class of problem, which they are already divided into.

2. The ``ignorable`` attributes are added later by using scripts.

3. The possible license id (like ``mit``) is predicted as the license ID of the match with the
   longest ``match_coverage``. This has to be manually verified in most cases.

4. If the rule is a ``false_positive`` as determined from the class of problem, only the
   ``is_false_positive`` attribute is there.

.. _crafted_rule_confidence:

Rule Confidence
---------------

Calculation of ``rule-confidence`` for manually checking only the low confidence errors.
