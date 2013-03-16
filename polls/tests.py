from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

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

class HomePageViewTest(TestCase):

    def test_root_url_shows_links_to_all_polls(self):
        # Set up some polls
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question="life, the universe and everything", pub_date=timezone.now())
        poll2.save()

        response = self.client.get('/')

        # Check that we've used the right template
        self.assertTemplateUsed(response, 'home.html')

        # Check that we've passed polls to the template
        polls_in_context = response.context['polls']
        self.assertEquals(list(polls_in_context), [poll1, poll2])

        # Check the poll names appear on the page
        self.assertIn(poll1.question, response.content)
        self.assertIn(poll2.question, response.content)

        # Check that the page also contains the urls to individual polls
        poll1_url = reverse('polls.views.poll', args=[poll1.id,])
        self.assertIn(poll1_url, response.content)
        poll2_url = reverse('polls.views.poll', args=[poll2.id,])
        self.assertIn(poll2_url, response.content)
