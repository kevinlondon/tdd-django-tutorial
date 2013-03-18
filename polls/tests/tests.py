from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from polls.models import Poll, Choice
from polls.forms import PollVoteForm

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
        self.assertIn('type="radio"', form.as_p())

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
