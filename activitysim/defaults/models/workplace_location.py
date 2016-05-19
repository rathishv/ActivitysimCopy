# ActivitySim
# See full license in LICENSE.txt.

import os
import orca

from activitysim import activitysim as asim
from .util.misc import add_dependent_columns


@orca.injectable()
def workplace_location_spec(configs_dir):
    f = os.path.join(configs_dir, 'configs', "workplace_location.csv")
    return asim.read_model_spec(f).fillna(0)


@orca.step()
def workplace_location_simulate(set_random_seed,
                                persons_merged,
                                workplace_location_spec,
                                skims,
                                destination_size_terms,
                                chunk_size):

    """
    The workplace location model predicts the zones in which various people will
    work.
    """

    # for now I'm going to generate a workplace location for everyone -
    # presumably it will not get used in downstream models for everyone -
    # it should depend on CDAP and mandatory tour generation as to whethrer
    # it gets used
    choosers = persons_merged.to_frame()
    alternatives = destination_size_terms.to_frame()

    # set the keys for this lookup - in this case there is a TAZ in the choosers
    # and a TAZ in the alternatives which get merged during interaction
    skims.set_keys("TAZ", "TAZ_r")
    # the skims will be available under the name "skims" for any @ expressions
    locals_d = {"skims": skims}

    # FIXME - HACK - only include columns actually used in spec (which we pathologically know)
    choosers = choosers[["income_segment", "TAZ", "mode_choice_logsums"]]

    choices = asim.interaction_simulate(choosers,
                                        alternatives,
                                        workplace_location_spec,
                                        skims=skims,
                                        locals_d=locals_d,
                                        sample_size=50,
                                        chunk_size=chunk_size)

    # FIXME - no need to reindex?
    choices = choices.reindex(persons_merged.index)

    print "Describe of choices:\n", choices.describe()
    orca.add_column("persons", "workplace_taz", choices)

    add_dependent_columns("persons", "persons_workplace")
