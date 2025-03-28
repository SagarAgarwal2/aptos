module CryptoLiteracy::LearningApp {

    use aptos_framework::signer;
    use aptos_framework::coin;
    use aptos_framework::aptos_coin::AptosCoin;

    /// Struct to store student details.
    struct Student has key, store {
        lessons_completed: u64, // Number of lessons completed
        total_rewards: u64,     // Total rewards earned
    }

    /// Function to register a student in the app.
    public fun register_student(student: &signer) {
        let new_student = Student {
            lessons_completed: 0,
            total_rewards: 0,
        };
        move_to(student, new_student);
    }

    /// Function to reward students for completing lessons.
    public fun reward_student(student: &signer, amount: u64) acquires Student {
        let s = borrow_global_mut<Student>(signer::address_of(student));
        let reward = coin::withdraw<AptosCoin>(student, amount);
        coin::deposit<AptosCoin>(signer::address_of(student), reward);
        
        // Update the student's reward record
        s.lessons_completed = s.lessons_completed + 1;
        s.total_rewards = s.total_rewards + amount;
    }
}
