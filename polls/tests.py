from django.test import TestCase
from django.utils import timezone
from polls.models import Poll

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
        self.assertEquals(len(all_polls_in_db), 1)
        only_poll_in_db = all_polls_in_db[0]
        self.assertEquals(only_poll_in_db, poll)

        # And check that it has saved its two attrbs, question and pub_date
        self.assertEquals(only_poll_in_db.question, poll.question)
        self.assertEquals(only_poll_in_db.pub_date, poll.pub_date)

