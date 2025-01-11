import datetime
from django.db import models
from django.utils import timezone

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        """
        Returns True if the question was published within the last day.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Returns True if the question has been published.
        """
        return self.pub_date <= timezone.now()

    def days_since_publication(self):
        """
        Returns the number of days since the question was published.
        """
        if self.pub_date:
            return (timezone.now() - self.pub_date).days
        return None

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    def increment_votes(self):
        """
        Increments the vote count for this choice.
        """
        self.votes += 1
        self.save()

    def reset_votes(self):
        """
        Resets the vote count for this choice to zero.
        """
        self.votes = 0
        self.save()