import openai
from datetime import datetime, timedelta

# Set up your OpenAI API credentials
openai.api_key = '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'


def generate_event_schedule(title, description, duration, due_date, color):
    prompt = f"Given the duration of {duration} minutes and the due date {due_date}, schedule the event '{title}' with the description '{description}'. The event will start at [start time] and end at [end time]."

    # Generate the schedule using the OpenAI API
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Extract the generated schedule from the API response
    generated_schedule = response.choices[0].text.strip()

    # Process the generated schedule to extract start time, end time, and title
    start_time_start = generated_schedule.find("start at ") + len("start at ")
    start_time_end = generated_schedule.find(" and end at")
    start_time = generated_schedule[start_time_start:start_time_end]

    end_time_start = generated_schedule.find("end at ") + len("end at ")
    end_time_end = generated_schedule.find(".", end_time_start)
    end_time = generated_schedule[end_time_start:end_time_end]

    title_start = generated_schedule.find("event '") + len("event '")
    title_end = generated_schedule.find("'", title_start)
    title = generated_schedule[title_start:title_end]

    # Convert due_date to datetime object
    due_datetime = datetime.strptime(due_date, "%Y-%m-%d")

    # Calculate start and end datetime based on duration
    start_datetime = due_datetime.replace(hour=10, minute=0)  # Set the desired start time
    end_datetime = start_datetime + timedelta(minutes=duration)

    # Format start and end datetime strings
    start_datetime_str = start_datetime.strftime("%Y-%m-%d %H:%M")
    end_datetime_str = end_datetime.strftime("%Y-%m-%d %H:%M")

    return title, description, start_datetime_str, end_datetime_str, color


# Example usage:
event_list = []

while True:
    title = input("Enter event title (or 'quit' to exit): ")
    if title == "quit":
        break

    description = input("Enter event description: ")
    duration = float(input("Enter event duration (in minutes): "))
    due_date = input("Enter event due date (YYYY-MM-DD): ")

    event = {
        "title": title,
        "description": description,
        "duration": duration,
        "due_date": due_date
    }

    event_list.append(event)

# Generate the schedule for each event
for event in event_list:
    title, start_time, end_time = generate_event_schedule(event['duration'], event['due_date'], event['title'], event['description'])
    print(f"\nGenerated Schedule for Event '{event['title']}':")
    print("Start Time:", start_time)
    print("End Time:", end_time)
    print("Title:", title)
