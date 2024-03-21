<template>
  <div class="test-wrapper">
    <aside class="sidebar">
      <div class="progress-bar" :style="{ width: progressBarWidth + '%' }"></div>
      <nav class="question-nav">
        <button v-for="(index) in questions" :key="index" class="question-nav-item">
          Otázka {{ index + 1 }}
        </button>
      </nav>
    </aside>
    <main class="question-content">
      <h1>2023 A</h1>
      <div v-for="(question, index) in questions" :key="index" class="question-block">
        <p class="question-text">{{ question.text }}</p>
        <ul class="answers-list">
          <li v-for="answer in question.answers" :key="answer[0]"
              :class="{
          'answer': true,
          //'correct': submissionAttempted && correctAnswers[index][answer[0]] === true,
          'incorrect': submissionAttempted && correctAnswers[index][answer[0]] === false
        }">
            <label>
              <input type="checkbox" :value="answer" @change="selectAnswer(index, answer)"
                     :disabled="submissionAttempted">
              {{ answer[1] }}
            </label>
          </li>
        </ul>
      </div>
      <div class="submit-wrapper">
        <button class="submit-button" @click="submitAnswers" :disabled="submissionAttempted">Submit Test</button>
      </div>
      <div v-if="submissionAttempted" id="incorrectCountDisplay%">
        Your points: {{ points }} / {{ maxPoints }} ( {{percentage}} % )
      </div>
      <!-- <div class="progress-bar" :style="{ width: percentage + '%' }"> </div>-->
    </main>
  </div>
</template>

<script>
export default {
  name: 'InteraktivnyTest',
  data() {
    return {
      questions: [],
      selectedAnswers: {},
      submissionAttempted: false,
      correctAnswers: {},
      points: 0,
      maxPoints: 0,
      percentage: 0,
      incorrectCount: 0

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
          this.maxPoints = this.questions.length * 4;

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
          this.selectedAnswers[questionIndex] = [...this.selectedAnswers[questionIndex]];
        } else {
          this.selectedAnswers[questionIndex].push(answer);
        }
      }
    },
    submitAnswers() {
      this.submissionAttempted = true;
      this.incorrectCount = 0;

      this.questions.forEach((question, questionIndex) => {
        this.correctAnswers[questionIndex] = {};

        question.answers.forEach((answer) => {
          const isSelected = this.selectedAnswers[questionIndex]?.includes(answer);
          const isCorrect = isSelected === answer[2];
          this.correctAnswers[questionIndex][answer[0]] = isCorrect;
          if(!isCorrect && isSelected) this.incorrectCount++;
        });

        const unselectedAnswers = question.answers.filter(
          (answer) => !(this.selectedAnswers[questionIndex]?.includes(answer))
        );
        unselectedAnswers.forEach((answer) => {
          if (!answer[2]) {
            this.correctAnswers[questionIndex][answer[0]] = true;
          }else{
            this.incorrectCount++;
          }
        });
      });
      this.points = this.maxPoints - this.incorrectCount;
      this.percentage = ((this.points / this.maxPoints) * 100).toFixed(2);
    }
  }
};

</script>

<style>
.test-wrapper {
  display: flex;
  background: #F4F4F7;
}

.sidebar {
  width: 200px;
  background: #7C4DFF;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-bar {
  height: 10px;
  background: yellow;
  width: 0;
  transition: width 0.3s ease;
}

.question-nav {
  width: 100%;
}

.question-nav-item {
  width: 100%;
  padding: 10px;
  text-align: left;
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
}

.question-nav-item:hover,
.question-nav-item:focus {
  background: rgba(255, 255, 255, 0.2);
}

.question-content {
  flex-grow: 1;
  padding: 20px;
  background: #fff;
}

.question-block {
  background: #F8F8FA;
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 8px;
}
.question-text {
  margin-bottom: 20px;
}

.answers-list {
  list-style: none;
  padding: 0;
  margin-top: 0;
}

.answer {
  margin-bottom: 10px;
}

.answer input[type="checkbox"] {
  margin-right: 10px;
}

.answer.correct {
  background-color: #d4edda;
}

.answer.incorrect {
  background-color: #f8d7da;
}

.submit-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.submit-button {
  padding: 10px 20px;
  background-color: #7C4DFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.submit-button:hover {
  background-color: #6841c9;
}
</style>
