import random
import string
from faker import Faker
from faker_vehicle import VehicleProvider


class Generator:
	class GeneratorOutOfItemsException(Exception):
		pass

	def __init__(self):
		pass

	def generate(self):
		pass


class RandomStringGenerator(Generator):
	class EmptyStringException(Exception):
		pass

	def __init__(self, length=10,
				 hasLowercase=True,
				 hasUppercase=False,
				 hasDigits=False):
		self.length = length
		self.hasLowercase = hasLowercase
		self.hasDigits = hasDigits
		self.hasUppercase = hasUppercase

	def generate(self):
		self.__validateChoices()
		choice = self.__getChoices()
		ran = ''.join(random.choices(choice, k=self.length))
		return ran

	def __getChoices(self):
		choice = ""
		if self.hasLowercase:
			choice += string.ascii_lowercase
		if self.hasUppercase:
			choice += string.ascii_uppercase
		if self.hasDigits:
			choice += string.digits
		return choice

	def __validateChoices(self):
		if (
				not self.hasLowercase and not self.hasUppercase and not self.hasDigits):
			raise self.EmptyStringException(
				"Random string can not be empty!")


class SequentialPatternGenerator(Generator):
	def __init__(self, pattern, chList):
		self.__pattern = pattern
		self.__chList = chList

	def generate(self):
		try:
			pick = self.__chList.pop(0)
			output = self.__trySub(self.__pattern, "%s", pick)
			return output
		except IndexError:
			raise self.GeneratorOutOfItemsException
	
	def __trySub(self, istr, pattern, sub):
		return istr.replace(pattern, str(sub))


class RandomIntegerGenerator(RandomStringGenerator):
	def __init__(self, imin, imax):
		super().__init__()
		self.imin = int(imin)
		self.imax = int(imax)

	def generate(self):
		ran = random.randint(self.imin, self.imax)
		return int(ran)


class RandomFloatGenerator(RandomStringGenerator):
	def __init__(self, fmin, fmax, decimals=2):
		super().__init__()
		self.__fmin = int(fmin)
		self.__fmax = int(fmax)
		self.__decimals = decimals

	def generate(self):
		ran = self.__fmin + (random.random() * (self.__fmax - self.__fmin))
		return round(float(ran), self.__decimals)


class SerialGenerator(Generator):
	def __init__(self, start=0, step=1):
		self.start = start
		self.step = step
		self.current = start

	def generate(self):
		output = self.current
		self.current += self.step
		return output


class ConstantGenerator(Generator):
	def __init__(self, value):
		self.__value = value

	def generate(self):
		return self.__value


class SetGenerator(Generator):
	def __init__(self, chSet, destructive=False):
		self.chSet = list(chSet)
		self.__destructive = destructive

	def generate(self):
		try:
			pick = random.choice(self.chSet)
			if self.__destructive:
				self.chSet.remove(pick)
			return pick
		except IndexError:
			raise self.GeneratorOutOfItemsException


class SequentialSetGenerator(Generator):
	def __init__(self, chSet):
		self.chSet = list(chSet)

	def generate(self):
		try:
			pick = self.chSet.pop(0)
			return pick
		except IndexError:
			raise self.GeneratorOutOfItemsException


class FakeFirstNameGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.first_name()
		return name


class FakeLastNameGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.last_name()
		return name


class FakeNameGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = f"{self.__faker.first_name()} {self.__faker.last_name()}"
		return name


class FakeCityGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.city()
		name = name.replace('\'', "")
		return name


class FakeCountryGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.country()
		name = name.replace('\'', "")
		return name


class FakeStreetGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.street_name()
		name = name.replace('\'', "")
		return name


class FakeEmailGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.email()
		name = name.replace('\'', "")
		return name


class FakeIPv4Generator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.ipv4()
		name = name.replace('\'', "")
		return name


class FakeIPv6Generator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.ipv6()
		name = name.replace('\'', "")
		return name


class FakeMacGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.mac_address()
		name = name.replace('\'', "")
		return name


class FakeUriGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.uri()
		name = name.replace('\'', "")
		return name


class FakeUrlGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.url()
		name = name.replace('\'', "")
		return name


class FakeUsernameGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.user_name()
		name = name.replace('\'', "")
		return name


class FakeCreditCardNumberGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.credit_card_number()
		name = name.replace('\'', "")
		return name


class FakeDateGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date()
		name = name.replace('\'', "")
		return name


class FakeCurrentDecadeDateGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_this_decade()
		return name


class FakeCurrentMonthDateGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_this_month()
		return name


class FakeCurrentYearDateGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_this_year()
		return name


class FakeDateTimeGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_time_ad()
		return str(name)


class FakeCurrentDecadeDateTimeGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_time_this_decade()
		return str(name)


class FakeCurrentMonthDateTimeGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_time_this_month()
		return str(name)


class FakeCurrentYearDateTimeGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.date_time_this_year()
		return str(name)


class FakeVehicleModelGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()
		self.__faker.add_provider(VehicleProvider)

	def generate(self):
		name = self.__faker.vehicle_model()
		name = name.replace('\'', "")
		return name


class FakeVehicleMakeGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()
		self.__faker.add_provider(VehicleProvider)

	def generate(self):
		name = self.__faker.vehicle_make()
		name = name.replace('\'', "")
		return name


class FakeLicensePlateGenerator(Generator):
	def __init__(self):
		self.__faker = Faker()

	def generate(self):
		name = self.__faker.license_plate()
		name = name.replace('\'', "")
		return name

class PrettyTimeGenerator(Generator):
	def __init__(self, imin, imax):
		self.__imin = imin
		self.__imax = imax
		self.secondsInMinute = 60
		self.secondsInHour = 60 * 60
		self.secondsInDay = 60 * 60 * 24

	def generate(self):
		time = random.randint(self.__imin, self.__imax)
		minutes = 0
		hours = 0
		days = 0

		while time >= self.secondsInDay:
			days += 1
			time -= self.secondsInDay
		while time >= self.secondsInHour:
			hours += 1
			time -= self.secondsInHour
		while time >= self.secondsInMinute:
			minutes += 1
			time -= self.secondsInMinute
		seconds = time

		timeStr = ""
		timeStr = self.__addValIfNotNone(timeStr, days, 'd');
		timeStr = self.__addValIfNotNone(timeStr, hours, 'h');
		timeStr = self.__addValIfNotNone(timeStr, minutes, 'm');
		timeStr = self.__addValIfNotNone(timeStr, seconds, 's');
		timeStr = timeStr[:-1]
		return timeStr

	def __addValIfNotNone(self, istr, val, affix):
		if val > 0:
			istr += str(val) + affix + " "
		return istr