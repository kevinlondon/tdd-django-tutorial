from collections import namedtuple
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PollInfo = namedtuple('PollInfo', ['question', 'choices'])
POLL1 = PollInfo(
    question="How awesome is Test-Driven Development?",
    choices=[
        "Very awesome",
        "Quite awesome",
        "Moderately awesome",
    ],
)
POLL2 = PollInfo(
    question="Which workshop treat do you prefer?",
    choices=[
        "Beer",
        "Pizza",
        "The Acquisition of Knowledge",
    ],
)


class PollsTest(LiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_poll_via_admin_site(self):
        # Opens web browser, goes to the admin page
        self.browser.get(self.live_server_url + '/admin/')

        # See familiar 'Django Administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # Type in username and passwords and hit return
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)

        # Login after success and land on Site Admin page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

        # See a few hyperlinks that say Polls
        polls_links = self.browser.find_elements_by_link_text('Polls')
        self.assertEquals(len(polls_links), 2)

        # Click second poll link
        polls_links[1].click()

        # She is taken to the polls listing page, which shows she has
        # no polls yet
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('0 polls', body.text)

        # Add a new poll.
        new_poll_link = self.browser.find_element_by_link_text('Add poll')
        new_poll_link.click()

        # See input fields for Question and Date Published
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Question:', body.text)
        self.assertIn('Date published:', body.text)

        # Add a question for the poll
        question_field = self.browser.find_element_by_name('question')
        question_field.send_keys('How awesome is Test-Driven Development?')

        # Set time and date of publication.
        date_field = self.browser.find_element_by_name('pub_date_0')
        date_field.send_keys('01/01/12')
        time_field = self.browser.find_element_by_name('pub_date_1')
        time_field.send_keys('00:00')

        # Enter additional choices for the poll.
        choice_1 = self.browser.find_element_by_name('choice_set-0-choice')
        choice_1.send_keys('Very awesome')
        choice_2 = self.browser.find_element_by_name('choice_set-1-choice')
        choice_2.send_keys('Quite awesome')
        choice_3 = self.browser.find_element_by_name('choice_set-2-choice')
        choice_3.send_keys('Moderately awesome')

        # Selects save.
        save_button = self.browser.find_element_by_css_selector("input[value='Save']")
        save_button.click()

        # Return to polls listing. See new poll.
        new_poll_links = self.browser.find_elements_by_link_text(
                "How awesome is Test-Driven Development?"
        )
        self.assertEquals(len(new_poll_links), 1)

    def _setup_polls_via_admin(self):
        # "Getrude logs into the admin site"
        self.browser.get(self.live_server_url + "/admin/")
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)

        # She has a number of polls to enter. For each one she:
        for poll_info in [POLL1, POLL2]:
            # Follows the link to the Polls app and adds a new Poll
            self.browser.find_elements_by_link_text('Polls')[1].click()
            self.browser.find_element_by_link_text('Add poll').click()

            # Enter its name, use 'today' and 'now' buttons to set pub date
            question_field = self.browser.find_element_by_name('question')
            question_field.send_keys(poll_info.question)
            self.browser.find_element_by_link_text('Today').click()
            self.browser.find_element_by_link_text('Now').click()

            # Sees she can enter choices for the Poll on the same page.
            for i, choice_text in enumerate(poll_info.choices):
                choice_field = self.browser.find_element_by_name('choice_set-%d-choice' % i)
                choice_field.send_keys(choice_text)

            # Save new poll.
            save_button = self.browser.find_element_by_css_selector('input[value="Save"]')
            save_button.click()

            # Is returned to the "Polls" listing, where she can see her new poll
            # listed as a callable link by its name.

            new_poll_links = self.browser.find_elements_by_link_text(
                    poll_info.question
            )
            self.assertEquals(len(new_poll_links), 1)

            # She goes back to the root of the admin site.
            self.browser.get(self.live_server_url + "/admin/")

        # She logs out of the admin site.
        self.browser.find_element_by_link_text('Log out').click()

    def test_voting_on_a_new_poll(self):
        # First Admin logs into the admin site and creates
        # a couple of new polls and their response choices.
        self._setup_polls_via_admin()

        # Now, another user goes to the homepage of the site.
        # He sees a list of polls.
        self.browser.get(self.live_server_url)
        heading = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(heading.text, 'Polls')

        # He clicks on the link to the first Poll, which is called
        # "How awesome is test-driven development?"
        first_poll_title = POLL1.question
        self.browser.find_element_by_link_text(first_poll_title).click()

        # He is taken to a poll 'results' page, which says
        # "No-one has voted on this poll yet."
        main_heading = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(main_heading.text, 'Poll Results')
        sub_heading = self.browser.find_element_by_tag_name('h2')
        self.assertEquals(sub_heading.text, first_poll_title)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('No-one has voted on this poll yet', body.text)

        # He also sees a form which offers him several choices.
        # He decides to select "very awesome"
        choice_inputs = self.browser.find_elements_by_css_selector(
                "input[type='radio']"
        )

        # The buttons have labels to explain them
        choice_labels = self.browser.find_elements_by_tag_name('label')
        choices_text = [c.text for c in choice_labels]
        self.assertEquals(choices_text, [
            "Vote:", # auto generated for the form
            'Very awesome',
            'Quite awesome',
            'Moderately awesome',
        ])

        # He selects "very awesome", which is answer number 1
        chosen = self.browser.find_element_by_css_selector(
                "input[value='1']"
        )
        chosen.click()

        # He clicks "submit"
        self.browser.find_element_by_css_selector("input[type='submit']").click()

        # The page refreshes, he sees that his choice has
        # updated the results. They now say
        # "100 %: very awesome".
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn("100 %: Very awesome", body_text)

        # The page also says "1 votes"
        self.assertIn('1 vote', body_text)

        # But not '1 votes'. It's singular.
        self.assertNotIn('1 votes', body_text)

        # User suspects site isn't well protected, so he tries to
        # do some "astroturfing"
        self.browser.find_element_by_css_selector("input[value='1']").click()
        self.browser.find_element_by_css_selector("input[type='submit']").click()

        # The page refreshes, he sees that his choice has updated the results.
        # It still says 100% very awesome.
        body_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("100 %: Very awesome", body_text)

        # But now page shows 2 votes
        self.assertIn("2 votes", body_text)

        # tries voting for a different choice
        self.browser.find_element_by_css_selector("input[value='2']").click()
        self.browser.find_element_by_css_selector("input[type='submit']").click()

        # Now percentage updates along with votes
        body_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("67 %: Very awesome", body_text)
        self.assertIn("33 %: Quite awesome", body_text)
        self.assertIn("3 votes", body_text)

        # The user is satisfied.
