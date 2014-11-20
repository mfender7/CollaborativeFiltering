from math import sqrt

class Filter(object):
    """
    this is going to be a really naive and as a result slow implementation
    of the filtering algorithm, its gonna be hella slow for more than proabably
    like 10 ratings/users

    eww
    """
    def __init__(self, table, rating):
        self.table = table
        self.rating = rating

    def similarity(self, user_id, other_id):
        """
        """
        with self.table.session_scope() as session:
            user = self.table.fetch_user_by_id(session, user_id)
            other = self.table.fetch_user_by_id(session, other_id)

            shared_courses = {course for course in user.courses if getattr(self.table.fetch_rating_by_id(session, user.user_id, course.course_id), self.rating) is not None} & {course for course in other.courses if getattr(self.table.fetch_rating_by_id(session, other.user_id, course.course_id), self.rating) is not None}
            user_rss = sqrt(sum(getattr(self.table.fetch_rating_by_id(session, user_id, course.course_id), self.rating) ** 2 for course in shared_courses))
            other_rss = sqrt(sum(getattr(self.table.fetch_rating_by_id(session, other_id, course.course_id), self.rating) ** 2 for course in shared_courses))
            multiplicative_sum = sum(getattr(self.table.fetch_rating_by_id(session, user_id, course.course_id), self.rating) * getattr(self.table.fetch_rating_by_id(session, other_id, course.course_id), self.rating) for course in shared_courses)
        return 0 if user_rss * other_rss == 0 else multiplicative_sum / (user_rss * other_rss)


    def calculated_rating(self, user_id, course_id):
        """
        """
        with self.table.session_scope() as session:
            user = self.table.fetch_user_by_id(session, user_id)
            users = {person for person in self.table.users}
            new_users = set()
            for person in users:
                try:
                    session.add(person)
                    new_users.add(person)
                except:
                    pass
            other_users = {other for other in new_users if user.school == other.school and getattr(self.table.fetch_rating_by_id(session, other.user_id, course_id), self.rating) is not None and other.user_id is not user_id}
            top = sum(self.similarity(user_id, other.user_id) * getattr(self.table.fetch_rating_by_id(session, other.user_id, course_id), self.rating) for other in other_users)
            bottom = sum(self.similarity(user_id, other.user_id) for other in other_users)
        return float(top)/float(bottom)