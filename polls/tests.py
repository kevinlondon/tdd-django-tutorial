from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from polls.models import Poll, Choice
from polls.forms import PollVoteForm

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

class SinglePollViewTest(TestCase):

    def test_page_shows_poll_title_and_no_votes_message(self):
        # Set up two polls, check the correct one is supplied
        poll1 = Poll(question="6 times 7", pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question="life, the universe and everything", pub_date=timezone.now())
        poll2.save()

        response = self.client.get("/poll/%d/" % (poll2.id, ))

        # Check we've used the poll template
        self.assertTemplateUsed(response, 'poll.html')

        # Check we've passed the right poll into the context
        self.assertEquals(response.context['poll'], poll2)

        # Check the poll's question properly appears on the page.
        self.assertIn(poll2.question, response.content)

        # Check our 'no votes yet' message appears
        self.assertIn("No-one has voted on this poll yet", response.content)


class PollsVoteFormTest(TestCase):

    def test_form_renders_poll_choices_as_radio_inputs(self):
        # Set up a poll with a couple of choices
        poll1 = Poll(question="6 times 7", pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="42", votes=0)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The Ultimate Answer", votes=0)
        choice2.save()

        # Set up another poll to make sure we only see the right choices
        poll2 = Poll(question="time", pub_date=timezone.now())
        poll2.save()
        choice3 = Choice(poll=poll2, choice="PM", votes=0)
        choice3.save()

        # Build a voting form for poll1
        form = PollVoteForm(poll=poll1)

        # Check it has a single field called 'vote' which has the right choices.
        self.assertEquals(form.fields.keys(), ['vote'])

        # Choices are tuples in the format (choice_number, choice_text)
        self.assertEquals(form.fields['vote'].choices, [
            (choice1.id, choice1.choice),
            (choice2.id, choice2.choice),
        ])

        # Check that it uses radio inputs to render
        self.assertIn('input type="radio"', form.as_p())

    def test_page_shows_choices_using_form(self):
        # Set up a poll with choices
        poll1 = Poll(question="time", pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="PM", votes=0)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="Gardener's", votes=0)
        choice2.save()

        response = self.client.get("/poll/%d/" % (poll1.id, ))

        # Check we've passed in a form of the right type
        self.assertTrue(isinstance(response.context['form'], PollVoteForm))

        # And check the form is being used in the template,
        # by checking for the choice text
        self.assertIn(choice1.choice, response.content.replace("&#39;", "'"))
        self.assertIn(choice2.choice, response.content.replace("&#39;", "'"))
