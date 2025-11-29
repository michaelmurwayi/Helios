from agent.GoalIntake import GoalIntake


if __name__ == "__main__":
    gi = GoalIntake()
    goal = gi.get_goal()
    print(f"Goal: {goal.raw_text}, Attack Type: {goal.goal_type}, Target: {goal.target}, Timestamp: {goal.timestamp}")