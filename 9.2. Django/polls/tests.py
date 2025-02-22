import datetime

from django.test import TestCase
from django.utils import timezone
from .models import Question, Choice
from django.urls import reverse

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_exactly_one_day_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1)
        exactly_one_day_old_question = Question(pub_date=time)
        self.assertIs(exactly_one_day_old_question.was_published_recently(), False)

    def test_was_published_recently_with_question_published_now(self):
        time = timezone.now()
        now_question = Question(pub_date=time)
        self.assertIs(now_question.was_published_recently(), True)

    def test_was_published_recently_with_question_published_23_hours_59_minutes_59_seconds_ago(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        almost_recent_question = Question(pub_date=time)
        self.assertIs(almost_recent_question.was_published_recently(), True)

    # def test_invalid_pub_date(self):
    #     with self.assertRaises(ValueError):
    #         Question(pub_date=None)

    def test_str_representation(self):
        question = Question(question_text="Sample Question", pub_date=timezone.now())
        self.assertEqual(str(question), "Sample Question")

    def test_is_published_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_past_question(self):
        time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.is_published(), True)

    def test_days_since_publication(self):
        time = timezone.now() - datetime.timedelta(days=5)
        question = Question(pub_date=time)
        self.assertEqual(question.days_since_publication(), 5)

    def test_days_since_publication_with_no_pub_date(self):
        question = Question(pub_date=None)
        self.assertIsNone(question.days_since_publication())

class ChoiceModelTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(question_text="Sample Question", pub_date=timezone.now())

    def test_str_representation(self):
        choice = Choice(question=self.question, choice_text="Choice A")
        self.assertEqual(str(choice), "Choice A")

    def test_increment_votes(self):
        choice = Choice(question=self.question, choice_text="Choice A")
        choice.save()
        choice.increment_votes()
        self.assertEqual(choice.votes, 1)

    def test_reset_votes(self):
        choice = Choice(question=self.question, choice_text="Choice A", votes=5)
        choice.save()
        choice.reset_votes()
        self.assertEqual(choice.votes, 0)

    def test_choice_belongs_to_question(self):
        choice = Choice(question=self.question, choice_text="Choice A")
        choice.save()
        self.assertEqual(choice.question, self.question)

    def test_choice_votes_default(self):
        choice = Choice(question=self.question, choice_text="Choice A")
        self.assertEqual(choice.votes, 0)