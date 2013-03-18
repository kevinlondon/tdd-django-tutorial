from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from polls.models import Poll, Choice
from polls.forms import PollVoteForm

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

