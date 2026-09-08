from pipeline import run_pipeline

TEST_TICKETS = [
    {"ticket_id": "T-1", "subject": "Duplicate charge", "body": "My card was charged twice for order #4521"},
    {"ticket_id": "T-2", "subject": "App keeps crashing", "body": "App crashes every time I try to log in"},
    {"ticket_id": "T-3", "subject": "Damaged item", "body": "I want to return this and get my money back, it's damaged"},
    {"ticket_id": "T-4", "subject": "Never received order", "body": "My order says delivered but I never got it"},
    {"ticket_id": "T-5", "subject": "Student discount?", "body": "Do you offer student discounts?"},
    {"ticket_id": "T-6", "subject": "THIRD TIME EMAILING", "body": "This is the THIRD time I've emailed you, absolutely useless service, I want a refund NOW"},
    {"ticket_id": "T-7", "subject": "Damaged + extra shipping charge", "body": "My package arrived damaged and also I was charged extra shipping I wasn't told about"},
    {"ticket_id": "T-8", "subject": "Help", "body": ""},
    {"ticket_id": "T-9", "subject": "Order not arrived", "body": "Mera order abhi tak nahi aya"},
    {"ticket_id": "T-10", "subject": "asdkjaslkdj", "body": "asdkjaslkdj free crypto click here"},
]

if __name__ == "__main__":
    print(f"Running {len(TEST_TICKETS)} test tickets through the pipeline...\n")
    for ticket in TEST_TICKETS:
        result = run_pipeline(**ticket)
        print(f"{result.ticket_id}: {result.category} (conf={result.confidence:.2f}) -> {result.action}"
              + (f" [{result.flagged_reason}]" if result.flagged_reason else ""))
    print("\nDone. Full details logged to results.csv")