<template>
  <div class="container">
    <h1>Test Questions</h1>
    <form @submit.prevent="submitAnswers">
      <div v-for="(question, index) in questions" :key="index" class="question">
        <p>{{ question.text }}</p>
        <ul>
          <li v-for="answer in question.answers" :key="answer[0]" class="answer">
            <label>
              <input type="checkbox" :value="answer" @change="selectAnswer(index, answer)">
              {{ answer[1] }}
            </label>
          </li>
        </ul>
      </div>
      <button type="submit">Submit</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'InteraktivnyTest',
  data() {
    return {
      questions: [],
      selectedAnswers: {},
    };
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    fetchQuestions() {
      fetch('http://localhost:8000/api/get_test_questions/')
        .then(response => response.json())
        .then(data => {
          this.questions = Object.entries(data).map(([key, value]) => ({
            ...value,
            id: key
          }));
        })
        .catch(error => {
          console.error('Fetching questions failed:', error);
        });
    },
    selectAnswer(questionIndex, answer) {
      if (!this.selectedAnswers[questionIndex]) {
        this.$set(this.selectedAnswers, questionIndex, [answer]);
      } else {
        const answerIndex = this.selectedAnswers[questionIndex].findIndex(selected => selected[0] === answer[0]);
        if (answerIndex > -1) {
          this.selectedAnswers[questionIndex].splice(answerIndex, 1);
          // Ensure reactivity for arrays
          this.selectedAnswers[questionIndex] = [...this.selectedAnswers[questionIndex]];
        } else {
          this.selectedAnswers[questionIndex].push(answer);
        }
      }
    },
    submitAnswers() {
      // Here you can process the selected answers as needed
      console.log(this.selectedAnswers);
    }
  }
};
</script>


<style>
.container {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.question, .answer {
  margin-bottom: 20px;
}

.label {
  cursor: pointer;
}

.correct {
  background-color: #c8e6c9; /* Green background for correct answers */
}

.selected {
  font-weight: bold;
}
</style>
