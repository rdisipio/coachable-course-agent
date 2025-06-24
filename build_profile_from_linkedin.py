from coachable_course_agent.agent_runner import create_profile_building_agent

def main():
    print("👋 Welcome to the Profile Builder!")
    print("This assistant will help you create a learning profile from your background.")

    # Step 1: Get user ID
    user_id = input("🆔 What is your user ID? ").strip()

    # Step 2: Get LinkedIn-style bio
    print("\n📝 Please paste your short bio or LinkedIn-style description below.")
    print("Example: 'I lead a product design team and want to improve my AI and UX strategy skills.'")
    blurb = input("📄 Your bio: ").strip()

    # Step 3: Format prompt
    prompt = f"My user ID is {user_id}. Here is my bio: {blurb}"

    # Step 4: Create and run the agent
    agent = create_profile_building_agent()
    agent.invoke({"input": prompt})


if __name__ == "__main__":
    main()