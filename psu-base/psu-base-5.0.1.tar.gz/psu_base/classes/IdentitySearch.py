from psu_base.services import error_service
from psu_base.classes.User import User
from psu_base.classes.Log import Log
from psu_base.classes.Finti import Finti

log = Log()


class SearchResults:
    keywords = None  # Remember the original search terms

    # Lists of User objects
    students = None
    employees = None
    others = None
    # If prioritizing, students will be copied into sub-categories
    registered_students = None
    unregistered_students = None

    # Finti will not return photos for large result sets
    photos_included = None
    # Certain user groups may have photos retrieved individually
    student_photos = None
    registered_student_photos = None
    employee_photos = None
    other_photos = None

    # Original number of results from Finti
    num_unfiltered_matches = None

    # Number of matches that were filtered out
    others_removed = 0

    @property
    def num_students(self):
        return len(self.students)

    @property
    def num_registered_students(self):
        return len(self.registered_students)

    @property
    def num_unregistered_students(self):
        return len(self.unregistered_students)

    @property
    def num_employees(self):
        return len(self.employees)

    @property
    def num_others(self):
        return len(self.others)

    @property
    def num_results(self):
        return self.num_employees + self.num_students + self.num_others

    @staticmethod
    def get_photo(identifier):
        """Get a single ID photo for a specified search result"""
        try:
            finti = Finti()
            photo = finti.get(f'wdt/v1/sso_proxy/auth/identity/{identifier}/photo')
            if finti.successful:
                return photo
        except Exception as ee:
            error_service.record(ee, identifier)

        return None

    def __init__(self, keywords, require_username=True):
        """Search for student via Finti"""
        log.trace([keywords])
        self.keywords = keywords

        # Get data from Finti APIs
        try:
            all_matches = Finti().get(f'wdt/v1/sso_proxy/identity/search', parameters={'keywords': keywords})
            self.num_unfiltered_matches = len(all_matches)

            # Eliminate duplicates by grouping by username or pidm
            if require_username:
                match_dict = {x.get('uid'): x for x in all_matches if x.get('uid')}
                del all_matches
            else:
                match_dict = {x.get('pidm'): x for x in all_matches if x.get('pidm')}
                del all_matches

            # Attempt to handle large result sets by prioritizing results
            self.students = []
            self.employees = []
            self.others = []

            employee_roles = [
                'EMPLOYEE', 'FACULTY'
            ]
            student_roles = [
                'STUDENT', 'REGISTERED_STUDENT', 'STUDENT_WORKER', 'SPONSORED_STUDENT', 'STUDENT_WORKER_ACTIVE_JOB',
                'NONACTIVE_STUDENT'
            ]

            for identifier, identity in match_dict.items():
                if not identity:
                    continue

                # Finti will only include photos for reasonable result set, and not everyone will have one.
                # Check for existence of photos. If one exists, they will exist for everyone who has one.
                if not self.photos_included:
                    self.photos_included = 'photo' in identity

                role_str = identity.get('eduPersonScopedAffiliation') if identity else None
                if role_str and any([rr in role_str for rr in employee_roles]):
                    self.employees.append(User(identity, get_authorities=False))
                elif role_str and any([rr in role_str for rr in student_roles]):
                    self.students.append(User(identity, get_authorities=False))
                else:
                    self.others.append(User(identity, get_authorities=False))
            del match_dict

            # If many "other" users, remove users with no roles, as long as others remain
            if self.num_others > 10:
                wr = [x for x in self.others if x.roles]
                num_with_roles = len(wr)
                # if at least 3 results are being removed
                if wr and self.num_others - num_with_roles >= 3:
                    self.others_removed = self.num_others - num_with_roles
                    self.others = wr
                del wr

            if self.students:
                self.students = sorted(self.students, key=lambda x: f"{x.last_name}, {x.first_name}")
            if self.employees:
                self.employees = sorted(self.employees, key=lambda x: f"{x.last_name}, {x.first_name}")
            if self.others:
                self.others = sorted(self.others, key=lambda x: f"{x.last_name}, {x.first_name}")

            # If photos were not included, but there are a reasonable number of filtered results, get some photos
            if self.photos_included:
                self.student_photos = self.registered_student_photos = self.employee_photos = self.other_photos = True
            else:
                if 0 < self.num_students < 10:
                    self.photos_included = 'SOME'
                    self.student_photos = self.registered_student_photos = True
                    for xx in self.students:
                        xx.id_photo = self.get_photo(xx.pidm)
                if 0 < self.num_employees < 10:
                    self.photos_included = 'SOME'
                    self.employee_photos = True
                    for xx in self.employees:
                        xx.id_photo = self.get_photo(xx.pidm)
                if 0 < self.num_others < 10:
                    self.photos_included = 'SOME'
                    self.other_photos = True
                    for xx in self.others:
                        xx.id_photo = self.get_photo(xx.pidm)

        except Exception as ee:
            error_service.unexpected_error("Unable to perform identity search", ee)

    def prioritize(self):
        """
        Copy student results into registered and unregistered categories.
        List "other" users with roles before those with no roles at all.
        Get photos of registered students if applicable
        """
        log.trace()

        # Prioritize registered students
        if self.students:
            self.registered_students = [x for x in self.students if 'registered_student' in x.roles]
            self.unregistered_students = [x for x in self.students if 'registered_student' not in x.roles]
        else:
            self.registered_students = []
            self.unregistered_students = []

        # Prioritize others with roles over others with no roles
        if self.others:
            wr = [x for x in self.others if x.roles]
            nr = [x for x in self.others if not x.roles]
            self.others = wr + nr
        else:
            self.others = []

        # If there is an exact match for username, bring it to the top and retrieve the photo if needed
        found = found_other = None
        if ' ' not in self.keywords:
            for tt, ll in {'R': self.registered_students, 'S': self.students, 'O': self.others}.items():
                for ii, student in enumerate(ll):
                    if self.keywords and student.username == self.keywords.lower():
                        found = ii
                        found_other = tt == 'O'
                        break
                if found is not None:
                    # Move to top of the list
                    ll.insert(0, ll.pop(found))
                    # Get the ID photo if needed
                    if not ll[0].id_photo:
                        ll[0].id_photo = self.get_photo(ll[0].username)
                        if ll[0].id_photo and not self.photos_included:
                            self.photos_included = 'SOME'
                    break

        if not self.student_photos:

            # If only a few are registered students, get their photos
            if self.registered_students and len(self.registered_students) <= 10:
                self.photos_included = 'SOME'
                self.registered_student_photos = True
                for ss in self.registered_students:
                    ss.id_photo = self.get_photo(ss.username)

            # If some students exist, and many "others" exist then ignore the others
            if self.num_students > 0 and self.num_others > 10:
                # If there was an exact username match, keep it
                if found_other:
                    found = self.others[0]
                    self.others = [found]
                else:
                    self.others = []
