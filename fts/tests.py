from django.test import LiveServerTestCase
from selenium import webdriver

class PollsTest(LiveServerTestCase):

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

        # Todo: Use the admin site to create a new Poll
        self.fail('todo: finish tests')
        
