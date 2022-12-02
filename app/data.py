from inspect import cleandoc
import pandas as pd
import numpy as np


class Study:
    """superclass for classes representing studies

    Subclasses have to provide a method `get_observation(rng, index)`, where
    `rng` is a NumPy random number generator instance and `index` is a
    zero-based index of the position of the observation in the current sample.
    It has to return a list containing the values of all variables in the
    current observation, where random values are created using `rng`.

    It is used by the method `get_sample(size, rng)` defined in this class,
    where `size` is the sample size and `rng` is the random number generator,
    which is passed on to `get_observation`. This method collects `size`
    observations and returns them as a pandas `DataFrame`, using information
    provided by `VARIABLES` (see below) for variable names and data types.

    Creating a sample one observation after another ensures that two samples
    (possibly of different size) based on the same state of `rng`, have the
    same observations at the beginning.

    In addition, subclasses have to provide four constant fields, whose values
    are exposed as properties defined in this class.

    `NAME`: the name of the study
        exposed as `name`

    `SHORT_DESCRIPTION`: a one-line description of the stud
        processed with `cleandoc` and exposed as `short_description`

    `ADDITIONAL_DESCRIPTION`: a longer multi-line description of the study
        processed with `cleandoc` and exposed as `additional_description`
        The web app processes this text as Markdown.

    `VARIABLES`: a dictionary where keys are variable names (in the order in
        which `get_sample` returns them; this assumes Python >= 3.7) and values
        are tuples containing 1) a data type recognized by pandas and 2) a
        short description of the variable (processed with `cleandoc`)
        exposed as `variables`

    Alternatively, each property can be redefined directly in the subclass.
    """

    def get_sample(self, size, rng):
        sample = [self.get_observation(rng, index) for index in range(size)]
        variables = {vn: vt for vn, (vt, vd) in self.variables.items()}
        df = pd.DataFrame.from_records(sample, columns=variables.keys())
        df = df.astype(variables)
        return df

    @property
    def name(self):
        return self.NAME

    @property
    def short_description(self):
        return cleandoc(self.SHORT_DESCRIPTION)

    @property
    def additional_description(self):
        return cleandoc(self.ADDITIONAL_DESCRIPTION)

    @property
    def variables(self):
        var = self.VARIABLES.copy()
        for vn in var:
            vt, vd = var[vn]
            var[vn] = (vt, cleandoc(vd))
        return var

    def get_values(self, variable_name):
        vt, _ = self.variables[variable_name]
        if str(vt) == 'category':
            return ', '.join(vt.categories)
        else:
            return None


class Simon (Study):

    NAME = 'Simon task'

    SHORT_DESCRIPTION = '''Reaction time depends on whether stimulus and
        response are on the same side.'''

    ADDITIONAL_DESCRIPTION = '''Participants are shown visual stimuli in a
        randomized sequence, out of a set of two different stimuli. They have
        to indicate which of the two stimuli is currently being presented, by
        pressing buttons on the left and right, with a mapping explained
        before. Each stimulus is either shown to the left or the right of a
        central fixation cross. A trial belongs to the 'congruent' condition if
        the correct response button is on the same side as the stimulus, and
        'incongruent' otherwise. Data are the per-subject average reaction
        times in ms for each of the two conditions. Each subject took part in
        the same experiment in two different sessions, a few days apart.

        Simulation based on the data of [Zwaan et al.
        (2018)](https://osf.io/ghv6m/).'''

    VARIABLES = {
        'session1_congruent': (
            float,
            'average reaction time in ms in congruent condition of session 1'),
        'session1_incongruent': (
            float,
            '''average reaction time in ms in incongruent condition of
            session 1'''),
        'session2_congruent': (
            float,
            'average reaction time in ms in congruent condition of session 2'),
        'session2_incongruent': (
            float,
            '''average reaction time in ms in incongruent condition of
            session 2''')
    }

    def __init__(self):
        # load data
        df = pd.read_csv('data/Zwaan2018/MeansSimonTask.csv')
        del df['participant']
        del df['similarity']
        # estimate simulation parameters from data
        self.mu = df.mean()
        self.Sigma = df.cov()

    def get_observation(self, rng, index):
        x = rng.multivariate_normal(self.mu, self.Sigma)
        return list(x)


class TwoSample (Study):

    NAME = 'Test: Two Samples'

    SHORT_DESCRIPTION = '''A variable is collected in participants
    alternately assigned to one of two different groups.'''

    ADDITIONAL_DESCRIPTION = 'No empirical basis.'

    @property
    def variables(self):
        return {
            'group': (
                pd.CategoricalDtype(self.groups, ordered=False),
                'independent variable'),
            'x': (
                float,
                'dependent variable')
        }

    def __init__(self, d):
        self.d = d
        self.groups = ['A', 'B']

    def get_observation(self, rng, index):
        gi = index % 2
        x = rng.normal()
        if gi == 1:
            x = x + self.d
        return [self.groups[gi], x]

    @property
    def name(self):
        return self.NAME + f' (d = {self.d})'


class Levels (Study):

    NAME = 'Measurement levels'

    SHORT_DESCRIPTION = 'Variables with different measurement levels.'

    ADDITIONAL_DESCRIPTION = 'No empirical basis.'

    @property
    def variables(self):
        return {
            'sex': (
                pd.CategoricalDtype(self.sex, ordered=False),
                'biological sex'),
            'happiness': (
                pd.CategoricalDtype(self.happiness, ordered=True),
                'self-rating of happiness'),
            'colour': (
                pd.CategoricalDtype(self.colour, ordered=False),
                'favourite colour'),
            'height': (
                float,
                'body height in cm')
        }

    def __init__(self):
        self.sex = ['female', 'male']
        self.happiness = ['very unhappy', 'unhappy', 'neutral',
                          'happy', 'very happy']
        self.colour = ['red', 'orange', 'yellow', 'green', 'blue', 'purple',
                       'black', 'white', 'grey', 'brown']
        # based on the ominous `diet.csv`
        self.sex_happiness = np.array([
            [0.16, 0.17, 0.09, 0.23, 0.35],
            [0.31, 0.26, 0.14, 0.18, 0.11]])
        self.sex_lhm = np.array([   # mean and std of log height
            [5.119, 0.05576],
            [5.163, 0.06775]])
        # based on
        #   <https://www.hotdesign.com/marketing/whats-your-favorite-color/>
        self.sex_colour = np.array([
            [0.120, 0.069, 0.060, 0.174, 0.260, 0.170, 0.064, 0.036, 0.032, 0.015],     # noqa E501
            [0.140, 0.080, 0.046, 0.200, 0.290, 0.090, 0.078, 0.026, 0.035, 0.015]])    # noqa E501

    def get_observation(self, rng, index):
        si = rng.integers(len(self.sex))
        hi = rng.choice(len(self.happiness), p=self.sex_happiness[si])
        ci = rng.choice(len(self.colour), p=self.sex_colour[si])
        height = np.round(np.exp(rng.normal(*self.sex_lhm[si])))
        return [self.sex[si], self.happiness[hi], self.colour[ci], height]
