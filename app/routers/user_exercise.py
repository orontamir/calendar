from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.models import User, UserExercise
from app.internal.utils import save


def create_user_exercise(session: Session, user: User) -> UserExercise:
    """
    Create and save new user exercise
    """
    if not does_user_exercise_exist(session=session, user_id=user.id):
        user_exercise = UserExercise(
            user_id=user.id,
            start_date=datetime.now()
            )
        save(user_exercise, session=session)
    else:
        user_exercise = update_user_exercise(session=session, user=user)
    return user_exercise


def does_user_exercise_exist(session: Session, user_id: int) -> bool:
    """
      Check if a user exercise for user id exists.
    """
    return get_user_exercise(session=session, user_id=user_id)



def get_user_exercise(session: Session, **param) -> list:
    """Returns user exercise filter by param."""
    try:
        user_exercise = list(session.query(UserExercise).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return user_exercise


def update_user_exercise(session: Session, user: User) -> UserExercise:
    user_ex = session.query(UserExercise).filter_by(user_id=user.id).first()
    # Update database
    user_ex.start_date = datetime.now()
    session.commit()
    return user_ex
