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

    def test_view_shows_percentage_of_votes(self):
        # Set up poll with choices.
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice='42', votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The Ultimate Answer", votes=2)
        choice2.save()

        response = self.client.get("/poll/%d/" % (poll1.id, ))

        # Check the percentage of votes are shown, sensibly rounded
        self.assertIn("33 %: 42", response.content)
        self.assertIn("67 %: The Ultimate Answer", response.content)

        # And that no-one has voted message is gone
        self.assertNotIn("No-one has voted", response.content)

    def test_view_can_handle_votes_via_POST(self):
        # Set up a poll with choices
        poll1 = Poll(question="6 times 7", pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="42", votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The Ultimate Answer", votes=3)
        choice2.save()

        # Set up our POST data. Keys and values are strings
        post_data = {'vote': str(choice2.id)}

        # Make our request to the view
        poll_url = "/poll/%d/" % (poll1.id, )
        response = self.client.post(poll_url, data=post_data)

        # Retrieve the updated choice from the db
        choice_in_db = Choice.objects.get(pk=choice2.id)

        # Check that its votes have gone up by 1.
        self.assertEquals(choice_in_db.votes, 4)

        # Always redirect after a post, even if we go back to the same page.
        self.assertRedirects(response, poll_url)

    def test_view_shows_total_votes(self):
        # Set up a poll with choices
        poll1 = Poll(question="6 times 7", pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="42", votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The Ultimate Answer", votes=2)
        choice2.save()

        response = self.client.get("/poll/%d/" % poll1.id)
        self.assertIn('3 votes', response.content)

        # Also check if we pluralise votes only when necessary
        choice2.votes = 0
        choice2.save()
        response = self.client.get('/poll/%d/' % poll1.id)
        self.assertIn('1 vote', response.content)
        self.assertNotIn('1 votes', response.content)
