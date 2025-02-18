import logging

from django.db import models

from betfair.models import Market, RunnerBook, Runner as BfRunner
from .managers import RaceManager, AccuracyManager, BucketManager, FixedOddManager, RunnerManager

logger = logging.getLogger(__name__)


class Meeting(models.Model):
    LOCATIONS = (
        ('QLD', 'Queensland'),
    )
    TYPES = (
        ('G', 'Grayhound'),
        ('R', 'Racing'),
        ('H', 'Harness'),
    )

    name = models.CharField(max_length=50)
    date = models.DateField()

    location = models.CharField(max_length=10, choices=LOCATIONS)
    race_type = models.CharField(max_length=1, choices=TYPES)
    rail_position = models.CharField(max_length=30, null=True)
    track_condition = models.CharField(max_length=30, null=True)
    venue_mnemonic = models.CharField(max_length=10)
    weather_condition = models.CharField(max_length=30, null=True)


class Race(models.Model):
    objects = RaceManager()

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    number = models.IntegerField()

    link_self = models.CharField(max_length=255)
    link_form = models.CharField(max_length=255, null=True)
    link_big_bets = models.CharField(max_length=255)
    distance = models.IntegerField()
    name = models.CharField(max_length=50)
    start_time = models.DateTimeField()

    direction = models.CharField(max_length=20, null=True)
    has_fixed_odds = models.BooleanField(default=True)
    has_parimutuel = models.BooleanField(default=True)
    class_conditions = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=20, null=True)
    number_of_places = models.IntegerField(null=True)

    has_results = models.BooleanField(default=False)
    has_processed = models.BooleanField(default=False)

    def __str__(self):
        return f'<Race [{self.id}] {self.meeting.name} R{self.number} time={self.start_time}>'

    @property
    def win_market(self):
        try:
            return self.market_set.filter(
                market_type='WIN'
            ).get()
        except:
            return None


class Runner(models.Model):
    objects = RunnerManager()

    race = models.ForeignKey(Race, on_delete=models.CASCADE)

    link_form = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=50)
    trainer_name = models.CharField(max_length=100, null=True)
    rider_name = models.CharField(max_length=100, null=True)
    runner_number = models.IntegerField()
    barrier_number = models.IntegerField()
    handicap_weight = models.FloatField(null=True)
    harness_handicap = models.FloatField(null=True)
    last_5_starts = models.CharField(max_length=5, null=True)
    dfs_form_rating = models.IntegerField(null=True)
    tech_form_rating = models.IntegerField(null=True)
    fixed_betting_status = models.CharField(max_length=20, null=True)
    parimutuel_betting_status = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f'<Runner num={self.runner_number} name={self.name}>'

    def fo(self):
        return self.fixedodd_set.all()[:5]

    def odds_change(self):
        first = self.fixedodd_set.first()
        last = list(self.fixedodd_set.all()[:5])[-1]
        first_perc = 1 / first.win_dec
        last_perc = 1 / last.win_dec
        return (first_perc - last_perc) / last_perc

    @property
    def rbook(self):
        if not hasattr(self, '_rbook'):
            self._rbook = None
            market = self.race.market_set.first()
            if market:
                book = market.book_set.last()
                try:
                    self._rbook = RunnerBook.objects.get(
                        book=book,
                        runner__cloth_number=self.runner_number
                    )
                except:
                    self._rbook = None
        return self._rbook

    @property
    def back(self):
        """Current betfair best available back odds"""
        if self.rbook:
            return self.rbook.lay_price

    @property
    def lay(self):
        """Current betfair best available back odds"""
        if self.rbook:
            return self.rbook.back_price

    @property
    def trade(self):
        """Current betfair best available back odds"""
        if self.rbook:
            if not self.rbook.last_price_traded:
                return None
            return self.rbook.last_price_traded


class FixedOdd(models.Model):
    objects = FixedOddManager()

    runner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    as_at = models.DateTimeField()
    win_dec = models.FloatField()
    place_dec = models.FloatField()

    class Meta:
        ordering = ['-as_at']

    @property
    def bucket(self):
        """Get bucket for current win odds"""
        return Bucket.objects.get_fo(self)

    @property
    def win_perc(self):
        return 1 / self.win_dec if self.win_dec else 0

    @property
    def win_est(self):
        """Give win est for given win_perc"""
        if not self.win_dec:
            return 0
        bucket = self.bucket
        est = bucket.coef * self.win_perc + bucket.intercept
        return max(0, min(1, est))

    @property
    def win_back(self):
        """Marked up with 30% to place a bet"""
        win_est = self.win_est
        if not win_est:
            return 0
        win_est *= 0.90
        return 1 / win_est

    @property
    def win_lay(self):
        """Marked up with 30% to place a bet"""
        win_est = self.win_est
        if not win_est:
            return 0
        win_est *= 1.10
        return 1 / win_est


class ParimutuelOdd(models.Model):
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    as_at = models.DateTimeField()
    win_dec = models.FloatField()
    place_dec = models.FloatField(null=True)

    class Meta:
        ordering = ['-as_at']


class Result(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    runner = models.OneToOneField(Runner, on_delete=models.CASCADE)
    pos = models.IntegerField()

    class Meta:
        ordering = ['pos']


class Accuracy(models.Model):
    objects = AccuracyManager()

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    runner = models.OneToOneField(Runner, on_delete=models.CASCADE)

    win_dec = models.FloatField(null=True)
    win_perc = models.FloatField(null=True)
    won = models.NullBooleanField()
    win_error = models.FloatField(null=True)

    place_dec = models.FloatField(null=True)
    place_perc = models.FloatField(null=True)
    place = models.NullBooleanField()
    place_error = models.FloatField(null=True)


class Bucket(models.Model):
    objects = BucketManager()

    bins = models.IntegerField()
    left = models.FloatField()
    right = models.FloatField()
    total = models.IntegerField()
    count = models.IntegerField()
    win_mean = models.FloatField()
    coef = models.FloatField()
    intercept = models.FloatField()
