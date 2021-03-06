from django.test import TestCase
from django.utils import timezone

from polls.models import Poll, Choice

class PollModelTest(TestCase):
    def test_creating_a_new_poll_and_saving_it_to_the_database(self):
        # Create a new poll object wiht its question set

        poll = Poll()
        poll.question = "What's up?"
        poll.pub_date = timezone.now()

        # Check if we can save it to the db
        poll.save()

        # Now check if we can find it in the db again
        all_polls_in_db = Poll.objects.all()
        self.assertEqual(len(all_polls_in_db), 1)
        only_poll_in_db = all_polls_in_db[0]
        self.assertEqual(only_poll_in_db, poll)

        # And check that it has saved its two attrbs, question and pub_date
        self.assertEqual(only_poll_in_db.question, poll.question)
        self.assertEqual(only_poll_in_db.pub_date, poll.pub_date)

    def test_verbose_name_for_pub_date(self):
        for field in Poll._meta.fields:
            if field.name == 'pub_date':
                self.assertEqual(field.verbose_name, 'Date published')

    def test_poll_objects_are_named_after_their_question(self):
        p = Poll()
        p.question = "How does theees work?"
        self.assertEqual(unicode(p), "How does theees work?")

    def test_poll_can_tell_you_its_total_votes(self):
        p = Poll(question="where", pub_date=timezone.now())
        p.save()
        c1 = Choice(poll=p, choice="here", votes=0)
        c1.save()
        c2 = Choice(poll=p, choice="there", votes=0)
        c2.save()

        self.assertEquals(p.total_votes(), 0)

        c1.votes = 1000
        c1.save()
        c2.votes = 22
        c2.save()
        self.assertEquals(p.total_votes(), 1022)

class ChoiceModelTest(TestCase):

    def test_create_some_choices_for_a_poll(self):
        # Create new poll object
        poll = Poll()
        poll.question = "What's up?"
        poll.pub_date = timezone.now()
        poll.save()

        # Create Choice object
        choice = Choice()
        choice.poll = poll
        choice.choice = "doin' fine..."

        # Give it faux votes
        choice.votes = 3
        choice.save()

        # Try to retrieve from DB using poll's reverse lookup.
        poll_choices = poll.choice_set.all()
        self.assertEquals(poll_choices.count(), 1)

        # Finally, check attrbs have been saved
        choice_from_db = poll_choices[0]
        self.assertEqual(choice_from_db, choice)
        self.assertEqual(choice_from_db.choice, "doin' fine...")
        self.assertEqual(choice_from_db.votes, 3)

    def test_choice_defaults(self):
        choice = Choice()
        self.assertEquals(choice.votes, 0)

    def test_choice_can_calculate_its_own_percentage_of_votes(self):
        poll = Poll(question="who?", pub_date=timezone.now())
        poll.save()
        choice1 = Choice(poll=poll, choice='me', votes=2)
        choice1.save()
        choice2 = Choice(poll=poll, choice="you", votes=1)
        choice2.save()

        self.assertEquals(choice1.percentage(), 100 * 2 / 3.0)
        self.assertEquals(choice2.percentage(), 100 * 1 / 3.0)

        # Also check 0 votes
        choice1.votes = 0
        choice1.save()
        choice2.votes = 0
        choice2.save()
        self.assertEquals(choice1.percentage(), 0)
        self.assertEquals(choice2.percentage(), 0)
