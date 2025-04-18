# -*- coding: UTF-8 -*-

from __future__ import absolute_import
from nose.tools import *

from behave import i18n, model, parser


class Common(object):
    def compare_steps(self, steps, expected):
        have = [(s.step_type, s.keyword, s.name, s.text, s.table) for s in steps]
        eq_(have, expected)


class TestParser(Common):
    def test_parses_feature_name(self):
        feature = parser.parse_feature("Feature: Stuff\n")
        eq_(feature.name, "Stuff")

    def test_parses_feature_name_without_newline(self):
        feature = parser.parse_feature("Feature: Stuff")
        eq_(feature.name, "Stuff")

    def test_parses_feature_description(self):
        doc = """
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(
            feature.description,
            ["In order to thing", "As an entity", "I want to do stuff"],
        )

    def test_parses_feature_with_a_tag(self):
        doc = """
@foo
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(
            feature.description,
            ["In order to thing", "As an entity", "I want to do stuff"],
        )
        eq_(feature.tags, [model.Tag("foo", 1)])

    def test_parses_feature_with_more_tags(self):
        doc = """
@foo @bar @baz @qux @winkle_pickers @number8
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(
            feature.description,
            ["In order to thing", "As an entity", "I want to do stuff"],
        )
        eq_(
            feature.tags,
            [
                model.Tag(name, 1)
                for name in ("foo", "bar", "baz", "qux", "winkle_pickers", "number8")
            ],
        )

    def test_parses_feature_with_a_tag_and_comment(self):
        doc = """
@foo    # Comment: ...
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(
            feature.description,
            ["In order to thing", "As an entity", "I want to do stuff"],
        )
        eq_(feature.tags, [model.Tag("foo", 1)])

    def test_parses_feature_with_more_tags_and_comment(self):
        doc = """
@foo @bar @baz @qux @winkle_pickers # Comment: @number8
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(
            feature.description,
            ["In order to thing", "As an entity", "I want to do stuff"],
        )
        eq_(
            feature.tags,
            [
                model.Tag(name, 1)
                for name in ("foo", "bar", "baz", "qux", "winkle_pickers")
            ],
        )
        # -- NOT A TAG: u'number8'

    def test_parses_feature_with_background(self):
        doc = """
Feature: Stuff
  Background:
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert feature.background
        self.compare_steps(
            feature.background.steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_feature_with_description_and_background(self):
        doc = """
Feature: Stuff
  This... is... STUFF!

  Background:
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(feature.description, ["This... is... STUFF!"])
        assert feature.background
        self.compare_steps(
            feature.background.steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_feature_with_a_scenario(self):
        doc = """
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_lowercase_step_keywords(self):
        doc = """
Feature: Stuff

  Scenario: Doing stuff
    giVeN there is stuff
    when I do stuff
    tHEn stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_ja_keywords(self):
        doc = """
機能: Stuff

  シナリオ: Doing stuff
    前提there is stuff
    もしI do stuff
    ならばstuff happens
""".lstrip()
        feature = parser.parse_feature(doc, language="ja")
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "前提", "there is stuff", None, None),
                ("when", "もし", "I do stuff", None, None),
                ("then", "ならば", "stuff happens", None, None),
            ],
        )

    def test_parses_feature_with_description_and_background_and_scenario(self):
        doc = """
Feature: Stuff
  Oh my god, it's full of stuff...

  Background:
    Given I found some stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])
        assert feature.background
        self.compare_steps(
            feature.background.steps,
            [
                ("given", "Given", "I found some stuff", None, None),
            ],
        )

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_feature_with_multiple_scenarios(self):
        doc = """
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens

  Scenario: Doing other stuff
    When stuff happens
    Then I am stuffed

  Scenario: Doing different stuff
    Given stuff
    Then who gives a stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")

        assert len(feature.scenarios) == 3

        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

        eq_(feature.scenarios[1].name, "Doing other stuff")
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("when", "When", "stuff happens", None, None),
                ("then", "Then", "I am stuffed", None, None),
            ],
        )

        eq_(feature.scenarios[2].name, "Doing different stuff")
        self.compare_steps(
            feature.scenarios[2].steps,
            [
                ("given", "Given", "stuff", None, None),
                ("then", "Then", "who gives a stuff", None, None),
            ],
        )

    def test_parses_feature_with_multiple_scenarios_with_tags(self):
        doc = """
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens

  @one_tag
  Scenario: Doing other stuff
    When stuff happens
    Then I am stuffed

  @lots @of @tags
  Scenario: Doing different stuff
    Given stuff
    Then who gives a stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")

        assert len(feature.scenarios) == 3

        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

        eq_(feature.scenarios[1].name, "Doing other stuff")
        eq_(feature.scenarios[1].tags, [model.Tag("one_tag", 1)])
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("when", "When", "stuff happens", None, None),
                ("then", "Then", "I am stuffed", None, None),
            ],
        )

        eq_(feature.scenarios[2].name, "Doing different stuff")
        eq_(
            feature.scenarios[2].tags, [model.Tag(n, 1) for n in ("lots", "of", "tags")]
        )
        self.compare_steps(
            feature.scenarios[2].steps,
            [
                ("given", "Given", "stuff", None, None),
                ("then", "Then", "who gives a stuff", None, None),
            ],
        )

    def test_parses_feature_with_multiple_scenarios_and_other_bits(self):
        doc = """
Feature: Stuff
  Stuffing

  Background:
    Given you're all stuffed

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens

  Scenario: Doing other stuff
    When stuff happens
    Then I am stuffed

  Scenario: Doing different stuff
    Given stuff
    Then who gives a stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(feature.description, ["Stuffing"])

        assert feature.background
        self.compare_steps(
            feature.background.steps,
            [("given", "Given", "you're all stuffed", None, None)],
        )

        assert len(feature.scenarios) == 3

        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

        eq_(feature.scenarios[1].name, "Doing other stuff")
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("when", "When", "stuff happens", None, None),
                ("then", "Then", "I am stuffed", None, None),
            ],
        )

        eq_(feature.scenarios[2].name, "Doing different stuff")
        self.compare_steps(
            feature.scenarios[2].steps,
            [
                ("given", "Given", "stuff", None, None),
                ("then", "Then", "who gives a stuff", None, None),
            ],
        )

    def test_parses_feature_with_a_scenario_with_and_and_but(self):
        doc = """
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    And some other stuff
    When I do stuff
    Then stuff happens
    But not the bad stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", None, None),
                ("given", "And", "some other stuff", None, None),
                ("when", "When", "I do stuff", None, None),
                ("then", "Then", "stuff happens", None, None),
                ("then", "But", "not the bad stuff", None, None),
            ],
        )

    def test_parses_feature_with_a_step_with_a_string_argument(self):
        doc = '''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So
      Much
      Stuff
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", "So\nMuch\nStuff", None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_string_argument_correctly_handle_whitespace(self):
        doc = '''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So
        Much
          Stuff
        Has
      Indents
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        string = "So\n  Much\n    Stuff\n  Has\nIndents"
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", string, None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_feature_with_a_step_with_a_string_with_blank_lines(self):
        doc = '''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So

      Much


      Stuff
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", "So\n\nMuch\n\n\nStuff", None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    # MORE-JE-ADDED:
    def test_parses_string_argument_without_stripping_empty_lines(self):
        # -- ISSUE 44: Parser removes comments in multiline text string.
        doc = '''
Feature: Multiline

  Scenario: Multiline Text with Comments
    Given a multiline argument with:
      """

      """
    And a multiline argument with:
      """
      Alpha.

      Omega.
      """
    Then empty middle lines are not stripped
'''.lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Multiline")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Multiline Text with Comments")
        text1 = ""
        text2 = "Alpha.\n\nOmega."
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "a multiline argument with", text1, None),
                ("given", "And", "a multiline argument with", text2, None),
                ("then", "Then", "empty middle lines are not stripped", None, None),
            ],
        )

    def test_parses_feature_with_a_step_with_a_string_with_comments(self):
        doc = '''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So
      Much
      # Derp
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "there is stuff", "So\nMuch\n# Derp", None),
                ("then", "Then", "stuff happens", None, None),
            ],
        )

    def test_parses_feature_with_a_step_with_a_table_argument(self):
        doc = """
Feature: Stuff

  Scenario: Doing stuff
    Given we classify stuff:
      | type of stuff | awesomeness | ridiculousness |
      | fluffy        | large       | frequent       |
      | lint          | low         | high           |
      | green         | variable    | awkward        |
    Then stuff is in buckets
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing stuff")
        table = model.Table(
            ["type of stuff", "awesomeness", "ridiculousness"],
            0,
            [
                ["fluffy", "large", "frequent"],
                ["lint", "low", "high"],
                ["green", "variable", "awkward"],
            ],
        )
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we classify stuff", None, table),
                ("then", "Then", "stuff is in buckets", None, None),
            ],
        )

    def test_parses_feature_with_table_and_escaped_pipe_in_cell_values(self):
        doc = """
Feature:
  Scenario:
    Given we have special cell values:
      | name   | value    |
      | alice  | one\|two |
      | bob    |\|one     |
      | charly |     one\||
      | doro   | one\|two\|three\|four |
""".lstrip()
        feature = parser.parse_feature(doc)
        assert len(feature.scenarios) == 1
        table = model.Table(
            ["name", "value"],
            0,
            [
                ["alice", "one|two"],
                ["bob", "|one"],
                ["charly", "one|"],
                ["doro", "one|two|three|four"],
            ],
        )
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we have special cell values", None, table),
            ],
        )

    def test_parses_feature_with_a_scenario_outline(self):
        doc = """
Feature: Stuff

  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
      | wood       | paper    |
      | explosives | hilarity |
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing all sorts of stuff")

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wool", "felt"],
                ["cotton", "thread"],
                ["wood", "paper"],
                ["explosives", "hilarity"],
            ],
        )
        eq_(feature.scenarios[0].examples[0].name, "Some stuff")
        eq_(feature.scenarios[0].examples[0].table, table)
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we have <Stuff>", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have <Things>", None, None),
            ],
        )

    def test_parses_feature_with_a_scenario_outline_with_multiple_examples(self):
        doc = """
Feature: Stuff

  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |

    Examples: Some other stuff
      | Stuff      | Things   |
      | wood       | paper    |
      | explosives | hilarity |
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing all sorts of stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we have <Stuff>", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have <Things>", None, None),
            ],
        )

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wool", "felt"],
                ["cotton", "thread"],
            ],
        )
        eq_(feature.scenarios[0].examples[0].name, "Some stuff")
        eq_(feature.scenarios[0].examples[0].table, table)

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wood", "paper"],
                ["explosives", "hilarity"],
            ],
        )
        eq_(feature.scenarios[0].examples[1].name, "Some other stuff")
        eq_(feature.scenarios[0].examples[1].table, table)

    def test_parses_feature_with_a_scenario_outline_with_tags(self):
        doc = """
Feature: Stuff

  @stuff @derp
  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
      | wood       | paper    |
      | explosives | hilarity |
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "Doing all sorts of stuff")
        eq_(feature.scenarios[0].tags, [model.Tag("stuff", 1), model.Tag("derp", 1)])
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we have <Stuff>", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have <Things>", None, None),
            ],
        )

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wool", "felt"],
                ["cotton", "thread"],
                ["wood", "paper"],
                ["explosives", "hilarity"],
            ],
        )
        eq_(feature.scenarios[0].examples[0].name, "Some stuff")
        eq_(feature.scenarios[0].examples[0].table, table)

    def test_parses_scenario_outline_with_tagged_examples1(self):
        # -- CASE: Examples with 1 tag-line (= 1 tag)
        doc = """
Feature: Alice

  @foo
  Scenario Outline: Bob
    Given we have <Stuff>

    @bar
    Examples: Charly
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Alice")

        assert len(feature.scenarios) == 1
        scenario_outline = feature.scenarios[0]
        eq_(scenario_outline.name, "Bob")
        eq_(scenario_outline.tags, [model.Tag("foo", 1)])
        self.compare_steps(
            scenario_outline.steps,
            [
                ("given", "Given", "we have <Stuff>", None, None),
            ],
        )

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wool", "felt"],
                ["cotton", "thread"],
            ],
        )
        eq_(scenario_outline.examples[0].name, "Charly")
        eq_(scenario_outline.examples[0].table, table)
        eq_(scenario_outline.examples[0].tags, [model.Tag("bar", 1)])

        # -- ScenarioOutline.scenarios:
        # Inherit tags from ScenarioOutline and Examples element.
        eq_(len(scenario_outline.scenarios), 2)
        expected_tags = [model.Tag("foo", 1), model.Tag("bar", 1)]
        eq_(set(scenario_outline.scenarios[0].tags), set(expected_tags))
        eq_(set(scenario_outline.scenarios[1].tags), set(expected_tags))

    def test_parses_scenario_outline_with_tagged_examples2(self):
        # -- CASE: Examples with multiple tag-lines (= 2 tag-lines)
        doc = """
Feature: Alice

  @foo
  Scenario Outline: Bob
    Given we have <Stuff>

    @bar
    @baz
    Examples: Charly
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Alice")

        assert len(feature.scenarios) == 1
        scenario_outline = feature.scenarios[0]
        eq_(scenario_outline.name, "Bob")
        eq_(scenario_outline.tags, [model.Tag("foo", 1)])
        self.compare_steps(
            scenario_outline.steps,
            [
                ("given", "Given", "we have <Stuff>", None, None),
            ],
        )

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wool", "felt"],
                ["cotton", "thread"],
            ],
        )
        eq_(scenario_outline.examples[0].name, "Charly")
        eq_(scenario_outline.examples[0].table, table)
        expected_tags = [model.Tag("bar", 1), model.Tag("baz", 1)]
        eq_(scenario_outline.examples[0].tags, expected_tags)

        # -- ScenarioOutline.scenarios:
        # Inherit tags from ScenarioOutline and Examples element.
        eq_(len(scenario_outline.scenarios), 2)
        expected_tags = [model.Tag("foo", 1), model.Tag("bar", 1), model.Tag("baz", 1)]
        eq_(set(scenario_outline.scenarios[0].tags), set(expected_tags))
        eq_(set(scenario_outline.scenarios[1].tags), set(expected_tags))

    def test_parses_feature_with_the_lot(self):
        doc = '''
# This one's got comments too.

@derp
Feature: Stuff
  In order to test my parser
  As a test runner
  I want to run tests

  # A møøse once bit my sister
  Background:
    Given this is a test

  @fred
  Scenario: Testing stuff
    Given we are testing
    And this is only a test
    But this is an important test
    When we test with a multiline string:
      """
      Yarr, my hovercraft be full of stuff.
      Also, I be feelin' this pirate schtick be a mite overdone, me hearties.
          Also: rum.
      """
    Then we want it to work

  #These comments are everywhere man
  Scenario Outline: Gosh this is long
    Given this is <length>
    Then we want it to be <width>
    But not <height>

    Examples: Initial
      | length | width | height |
# I don't know why this one is here
      | 1      | 2     | 3      |
      | 4      | 5     | 6      |

    Examples: Subsequent
      | length | width | height |
      | 7      | 8     | 9      |

  Scenario: This one doesn't have a tag
    Given we don't have a tag
    Then we don't really mind

  @stuff @derp
  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff with a table:
      | a | b | c | d | e |
      | 1 | 2 | 3 | 4 | 5 |
                             # I can see a comment line from here
      | 6 | 7 | 8 | 9 | 10 |
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
      | wood       | paper    |
      | explosives | hilarity |
'''.lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Stuff")
        eq_(feature.tags, [model.Tag("derp", 1)])
        eq_(
            feature.description,
            ["In order to test my parser", "As a test runner", "I want to run tests"],
        )

        assert feature.background
        self.compare_steps(
            feature.background.steps, [("given", "Given", "this is a test", None, None)]
        )

        assert len(feature.scenarios) == 4

        eq_(feature.scenarios[0].name, "Testing stuff")
        eq_(feature.scenarios[0].tags, [model.Tag("fred", 1)])
        string = "\n".join(
            [
                "Yarr, my hovercraft be full of stuff.",
                "Also, I be feelin' this pirate schtick be a mite overdone, "
                + "me hearties.",
                "    Also: rum.",
            ]
        )
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we are testing", None, None),
                ("given", "And", "this is only a test", None, None),
                ("given", "But", "this is an important test", None, None),
                ("when", "When", "we test with a multiline string", string, None),
                ("then", "Then", "we want it to work", None, None),
            ],
        )

        eq_(feature.scenarios[1].name, "Gosh this is long")
        eq_(feature.scenarios[1].tags, [])
        table = model.Table(
            ["length", "width", "height"],
            0,
            [
                ["1", "2", "3"],
                ["4", "5", "6"],
            ],
        )
        eq_(feature.scenarios[1].examples[0].name, "Initial")
        eq_(feature.scenarios[1].examples[0].table, table)
        table = model.Table(
            ["length", "width", "height"],
            0,
            [
                ["7", "8", "9"],
            ],
        )
        eq_(feature.scenarios[1].examples[1].name, "Subsequent")
        eq_(feature.scenarios[1].examples[1].table, table)
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("given", "Given", "this is <length>", None, None),
                ("then", "Then", "we want it to be <width>", None, None),
                ("then", "But", "not <height>", None, None),
            ],
        )

        eq_(feature.scenarios[2].name, "This one doesn't have a tag")
        eq_(feature.scenarios[2].tags, [])
        self.compare_steps(
            feature.scenarios[2].steps,
            [
                ("given", "Given", "we don't have a tag", None, None),
                ("then", "Then", "we don't really mind", None, None),
            ],
        )

        table = model.Table(
            ["Stuff", "Things"],
            0,
            [
                ["wool", "felt"],
                ["cotton", "thread"],
                ["wood", "paper"],
                ["explosives", "hilarity"],
            ],
        )
        eq_(feature.scenarios[3].name, "Doing all sorts of stuff")
        eq_(feature.scenarios[3].tags, [model.Tag("stuff", 1), model.Tag("derp", 1)])
        eq_(feature.scenarios[3].examples[0].name, "Some stuff")
        eq_(feature.scenarios[3].examples[0].table, table)
        table = model.Table(
            ["a", "b", "c", "d", "e"],
            0,
            [
                ["1", "2", "3", "4", "5"],
                ["6", "7", "8", "9", "10"],
            ],
        )
        self.compare_steps(
            feature.scenarios[3].steps,
            [
                ("given", "Given", "we have <Stuff>", None, None),
                ("when", "When", "we do stuff with a table", None, table),
                ("then", "Then", "we have <Things>", None, None),
            ],
        )

    def test_fails_to_parse_when_and_is_out_of_order(self):
        doc = """
Feature: Stuff

  Scenario: Failing at stuff
    And we should fail
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)

    def test_fails_to_parse_when_but_is_out_of_order(self):
        doc = """
Feature: Stuff

  Scenario: Failing at stuff
    But we shall fail
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)

    def test_fails_to_parse_when_examples_is_in_the_wrong_place(self):
        doc = """
Feature: Stuff

  Scenario: Failing at stuff
    But we shall fail

    Examples: Failure
      | Fail | Wheel|
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)


class TestForeign(Common):
    def test_first_line_comment_sets_language(self):
        doc = """
# language: fr
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_multiple_language_comments(self):
        # -- LAST LANGUAGE is used.
        doc = """
# language: en
# language: fr
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_language_comment_wins_over_commandline(self):
        doc = """
# language: fr
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc, language="de")
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_whitespace_before_first_line_comment_still_sets_language(self):
        doc = """


# language: cs
Po\u017eadavek: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_anything_before_language_comment_makes_it_not_count(self):
        doc = """

@wombles
# language: cy-GB
Arwedd: testing stuff
  Oh my god, it's full of stuff...
"""

        assert_raises(parser.ParserError, parser.parse_feature, doc)

    def test_defaults_to_DEFAULT_LANGUAGE(self):
        feature_kwd = i18n.languages[parser.DEFAULT_LANGUAGE]["feature"][0]
        doc = (
            """

@wombles
# language: cs
%s: testing stuff
  Oh my god, it's full of stuff...
"""
            % feature_kwd
        )

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_whitespace_in_the_language_comment_is_flexible_1(self):
        doc = """
#language:da
Egenskab: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_whitespace_in_the_language_comment_is_flexible_2(self):
        doc = """
# language:de
Funktionalit\xe4t: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_whitespace_in_the_language_comment_is_flexible_3(self):
        doc = """
#language: en-lol
OH HAI: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_whitespace_in_the_language_comment_is_flexible_4(self):
        doc = """
#       language:     lv
F\u012b\u010da: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

    def test_parses_french(self):
        doc = """
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...

  Contexte:
    Soit I found some stuff

  Sc\xe9nario: test stuff
    Soit I am testing stuff
    Alors it should work

  Sc\xe9nario: test more stuff
    Soit I am testing stuff
    Alors it will work
""".lstrip()
        feature = parser.parse_feature(doc, "fr")
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])
        assert feature.background
        self.compare_steps(
            feature.background.steps,
            [
                ("given", "Soit", "I found some stuff", None, None),
            ],
        )

        assert len(feature.scenarios) == 2
        eq_(feature.scenarios[0].name, "test stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Soit", "I am testing stuff", None, None),
                ("then", "Alors", "it should work", None, None),
            ],
        )

    def test_parses_french_multi_word(self):
        doc = """
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...

  Sc\xe9nario: test stuff
    Etant donn\xe9 I am testing stuff
    Alors it should work
""".lstrip()
        feature = parser.parse_feature(doc, "fr")
        eq_(feature.name, "testing stuff")
        eq_(feature.description, ["Oh my god, it's full of stuff..."])

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "test stuff")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Etant donn\xe9", "I am testing stuff", None, None),
                ("then", "Alors", "it should work", None, None),
            ],
        )

    test_parses_french_multi_word.go = 1

    def test_properly_handles_whitespace_on_keywords_that_do_not_want_it(self):
        doc = """
# language: zh-TW

\u529f\u80fd: I have no idea what I'm saying

  \u5834\u666f: No clue whatsoever
    \u5047\u8a2dI've got no idea
    \u7576I say things
    \u800c\u4e14People don't understand
    \u90a3\u9ebcPeople should laugh
    \u4f46\u662fI should take it well
"""

        feature = parser.parse_feature(doc)
        eq_(feature.name, "I have no idea what I'm saying")

        eq_(len(feature.scenarios), 1)
        eq_(feature.scenarios[0].name, "No clue whatsoever")
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "\u5047\u8a2d", "I've got no idea", None, None),
                ("when", "\u7576", "I say things", None, None),
                ("when", "\u800c\u4e14", "People don't understand", None, None),
                ("then", "\u90a3\u9ebc", "People should laugh", None, None),
                ("then", "\u4f46\u662f", "I should take it well", None, None),
            ],
        )


class TestParser4ScenarioDescription(Common):
    def test_parse_scenario_description(self):
        doc = """
Feature: Scenario Description

  Scenario: With scenario description

    First line of scenario description.
    Second line of scenario description.

    Third line of scenario description (after an empty line).

      Given we have stuff
      When we do stuff
      Then we have things
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Scenario Description")

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "With scenario description")
        eq_(feature.scenarios[0].tags, [])
        eq_(
            feature.scenarios[0].description,
            [
                "First line of scenario description.",
                "Second line of scenario description.",
                "Third line of scenario description (after an empty line).",
            ],
        )
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we have stuff", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have things", None, None),
            ],
        )

    def test_parse_scenario_with_description_but_without_steps(self):
        doc = """
Feature: Scenario Description

  Scenario: With description but without steps

    First line of scenario description.
    Second line of scenario description.

  Scenario: Another one
      Given we have stuff
      When we do stuff
      Then we have things
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Scenario Description")

        assert len(feature.scenarios) == 2
        eq_(feature.scenarios[0].name, "With description but without steps")
        eq_(feature.scenarios[0].tags, [])
        eq_(
            feature.scenarios[0].description,
            [
                "First line of scenario description.",
                "Second line of scenario description.",
            ],
        )
        eq_(feature.scenarios[0].steps, [])

        eq_(feature.scenarios[1].name, "Another one")
        eq_(feature.scenarios[1].tags, [])
        eq_(feature.scenarios[1].description, [])
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("given", "Given", "we have stuff", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have things", None, None),
            ],
        )

    def test_parse_scenario_with_description_but_without_steps_followed_by_scenario_with_tags(
        self,
    ):
        doc = """
Feature: Scenario Description

  Scenario: With description but without steps

    First line of scenario description.
    Second line of scenario description.

  @foo @bar
  Scenario: Another one
      Given we have stuff
      When we do stuff
      Then we have things
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Scenario Description")

        assert len(feature.scenarios) == 2
        eq_(feature.scenarios[0].name, "With description but without steps")
        eq_(feature.scenarios[0].tags, [])
        eq_(
            feature.scenarios[0].description,
            [
                "First line of scenario description.",
                "Second line of scenario description.",
            ],
        )
        eq_(feature.scenarios[0].steps, [])

        eq_(feature.scenarios[1].name, "Another one")
        eq_(feature.scenarios[1].tags, ["foo", "bar"])
        eq_(feature.scenarios[1].description, [])
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("given", "Given", "we have stuff", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have things", None, None),
            ],
        )

    def test_parse_two_scenarios_with_description(self):
        doc = """
Feature: Scenario Description

  Scenario: One with description but without steps

    First line of scenario description.
    Second line of scenario description.

  Scenario: Two with description and with steps

    Another line of scenario description.

      Given we have stuff
      When we do stuff
      Then we have things
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Scenario Description")

        assert len(feature.scenarios) == 2
        eq_(feature.scenarios[0].name, "One with description but without steps")
        eq_(feature.scenarios[0].tags, [])
        eq_(
            feature.scenarios[0].description,
            [
                "First line of scenario description.",
                "Second line of scenario description.",
            ],
        )
        eq_(feature.scenarios[0].steps, [])

        eq_(feature.scenarios[1].name, "Two with description and with steps")
        eq_(feature.scenarios[1].tags, [])
        eq_(
            feature.scenarios[1].description,
            [
                "Another line of scenario description.",
            ],
        )
        self.compare_steps(
            feature.scenarios[1].steps,
            [
                ("given", "Given", "we have stuff", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have things", None, None),
            ],
        )


def parse_tags(line):
    the_parser = parser.Parser()
    return the_parser.parse_tags(line.strip())


class TestParser4Tags(Common):
    def test_parse_tags_with_one_tag(self):
        tags = parse_tags("@one  ")
        eq_(len(tags), 1)
        eq_(tags[0], "one")

    def test_parse_tags_with_more_tags(self):
        tags = parse_tags("@one  @two.three-four  @xxx")
        eq_(len(tags), 3)
        eq_(tags, [model.Tag(name, 1) for name in ("one", "two.three-four", "xxx")])

    def test_parse_tags_with_tag_and_comment(self):
        tags = parse_tags("@one  # @fake-tag-in-comment xxx")
        eq_(len(tags), 1)
        eq_(tags[0], "one")

    def test_parse_tags_with_tags_and_comment(self):
        tags = parse_tags("@one  @two.three-four  @xxx # @fake-tag-in-comment xxx")
        eq_(len(tags), 3)
        eq_(tags, [model.Tag(name, 1) for name in ("one", "two.three-four", "xxx")])

    @raises(parser.ParserError)
    def test_parse_tags_with_invalid_tags(self):
        parse_tags("@one  invalid.tag boom")


class TestParser4Background(Common):
    def test_parse_background(self):
        doc = """
Feature: Background

  A feature description line 1.
  A feature description line 2.

  Background: One
    Given we init stuff
    When we init more stuff

  Scenario: One
    Given we have stuff
    When we do stuff
    Then we have things
""".lstrip()
        feature = parser.parse_feature(doc)
        eq_(feature.name, "Background")
        eq_(
            feature.description,
            [
                "A feature description line 1.",
                "A feature description line 2.",
            ],
        )
        assert feature.background is not None
        eq_(feature.background.name, "One")
        self.compare_steps(
            feature.background.steps,
            [
                ("given", "Given", "we init stuff", None, None),
                ("when", "When", "we init more stuff", None, None),
            ],
        )

        assert len(feature.scenarios) == 1
        eq_(feature.scenarios[0].name, "One")
        eq_(feature.scenarios[0].tags, [])
        self.compare_steps(
            feature.scenarios[0].steps,
            [
                ("given", "Given", "we have stuff", None, None),
                ("when", "When", "we do stuff", None, None),
                ("then", "Then", "we have things", None, None),
            ],
        )

    def test_parse_background_with_tags_should_fail(self):
        doc = """
Feature: Background with tags
  Expect that a ParserError occurs
  because Background does not support tags/tagging.

  @tags_are @not_supported
  @here
  Background: One
    Given we init stuff
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)

    def test_parse_two_background_should_fail(self):
        doc = """
Feature: Two Backgrounds
  Expect that a ParserError occurs
  because at most one Background is supported.

  Background: One
    Given we init stuff

  Background: Two
    When we init more stuff
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)

    def test_parse_background_after_scenario_should_fail(self):
        doc = """
Feature: Background after Scenario
  Expect that a ParserError occurs
  because Background is only allowed before any Scenario.

  Scenario: One
    Given we have stuff

  Background: Two
    When we init more stuff
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)

    def test_parse_background_after_scenario_outline_should_fail(self):
        doc = """
Feature: Background after ScenarioOutline
  Expect that a ParserError occurs
  because Background is only allowed before any ScenarioOuline.
  Scenario Outline: ...
    Given there is <name>

    Examples:
      | name  |
      | Alice |

  Background: Two
    When we init more stuff
""".lstrip()
        assert_raises(parser.ParserError, parser.parse_feature, doc)


class TestParser4Steps(Common):
    """
    Tests parser.parse_steps() and parser.Parser.parse_steps() functionality.
    """

    def test_parse_steps_with_simple_steps(self):
        doc = """
Given a simple step
When I have another simple step
 And I have another simple step
Then every step will be parsed without errors
""".lstrip()
        steps = parser.parse_steps(doc)
        eq_(len(steps), 4)
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        self.compare_steps(
            steps,
            [
                ("given", "Given", "a simple step", None, None),
                ("when", "When", "I have another simple step", None, None),
                ("when", "And", "I have another simple step", None, None),
                (
                    "then",
                    "Then",
                    "every step will be parsed without errors",
                    None,
                    None,
                ),
            ],
        )

    def test_parse_steps_with_multiline_text(self):
        doc = '''
Given a step with multi-line text:
    """
    Lorem ipsum
    Ipsum lorem
    """
When I have a step with multi-line text:
    """
    Ipsum lorem
    Lorem ipsum
    """
Then every step will be parsed without errors
'''.lstrip()
        steps = parser.parse_steps(doc)
        eq_(len(steps), 3)
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        text1 = "Lorem ipsum\nIpsum lorem"
        text2 = "Ipsum lorem\nLorem ipsum"
        self.compare_steps(
            steps,
            [
                ("given", "Given", "a step with multi-line text", text1, None),
                ("when", "When", "I have a step with multi-line text", text2, None),
                (
                    "then",
                    "Then",
                    "every step will be parsed without errors",
                    None,
                    None,
                ),
            ],
        )

    def test_parse_steps_when_last_step_has_multiline_text(self):
        doc = '''
Given a simple step
Then the last step has multi-line text:
    """
    Lorem ipsum
    Ipsum lorem
    """
'''.lstrip()
        steps = parser.parse_steps(doc)
        eq_(len(steps), 2)
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        text2 = "Lorem ipsum\nIpsum lorem"
        self.compare_steps(
            steps,
            [
                ("given", "Given", "a simple step", None, None),
                ("then", "Then", "the last step has multi-line text", text2, None),
            ],
        )

    def test_parse_steps_with_table(self):
        doc = """
Given a step with a table:
    | Name  | Age |
    | Alice |  12 |
    | Bob   |  23 |
When I have a step with a table:
    | Country | Capital |
    | France  | Paris   |
    | Germany | Berlin  |
    | Spain   | Madrid  |
    | USA     | Washington |
Then every step will be parsed without errors
""".lstrip()
        steps = parser.parse_steps(doc)
        eq_(len(steps), 3)
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        table1 = model.Table(
            ["Name", "Age"],
            0,
            [
                ["Alice", "12"],
                ["Bob", "23"],
            ],
        )
        table2 = model.Table(
            ["Country", "Capital"],
            0,
            [
                ["France", "Paris"],
                ["Germany", "Berlin"],
                ["Spain", "Madrid"],
                ["USA", "Washington"],
            ],
        )
        self.compare_steps(
            steps,
            [
                ("given", "Given", "a step with a table", None, table1),
                ("when", "When", "I have a step with a table", None, table2),
                (
                    "then",
                    "Then",
                    "every step will be parsed without errors",
                    None,
                    None,
                ),
            ],
        )

    def test_parse_steps_when_last_step_has_a_table(self):
        doc = """
Given a simple step
Then the last step has a final table:
    | Name   | City |
    | Alonso | Barcelona |
    | Bred   | London  |
""".lstrip()
        steps = parser.parse_steps(doc)
        eq_(len(steps), 2)
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        table2 = model.Table(
            ["Name", "City"],
            0,
            [
                ["Alonso", "Barcelona"],
                ["Bred", "London"],
            ],
        )
        self.compare_steps(
            steps,
            [
                ("given", "Given", "a simple step", None, None),
                ("then", "Then", "the last step has a final table", None, table2),
            ],
        )

    @raises(parser.ParserError)
    def test_parse_steps_with_malformed_table(self):
        doc = """
Given a step with a malformed table:
    | Name   | City |
    | Alonso | Barcelona | 2004 |
    | Bred   | London    | 2010 |
""".lstrip()
        steps = parser.parse_steps(doc)
