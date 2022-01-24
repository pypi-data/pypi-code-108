from wpilib import DriverStation, TimedRobot, reportError
from commands1 import Scheduler


class CommandBasedRobot(TimedRobot):
    """
    The base class for a Command-Based Robot. To use, instantiate commands and
    trigger them.
    """

    def startCompetition(self):
        """Initalizes the scheduler before starting robotInit()"""

        self.scheduler = Scheduler.getInstance()
        super().startCompetition()

    def commandPeriodic(self):
        """
        Run the scheduler regularly. If an error occurs during a competition,
        prevent it from crashing the program.
        """

        try:
            self.scheduler.run()
        except Exception as error:
            if not DriverStation.isFMSAttached():
                raise

            """Just to be safe, stop all running commands."""
            self.scheduler.removeAll()

            self.handleCrash(error)

    autonomousPeriodic = commandPeriodic
    teleopPeriodic = commandPeriodic
    disabledPeriodic = commandPeriodic
    # testPeriodic deliberately omitted

    def handleCrash(self, error):
        """
        Called if an exception is raised in the Scheduler during a competition.
        Writes an error message to the driver station by default. If you want
        more complex behavior, override this method in your robot class.
        """

        reportError(str(error), printTrace=True)
