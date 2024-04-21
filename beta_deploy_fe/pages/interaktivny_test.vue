<template>
  <div class="test-wrapper">
    <aside class="sidebar">
      <button class="home-button" @click="navigateHome">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>
      </button>
      <nav class="question-nav">
        <button
          v-for="(question, index) in questions"
          :key="question.id"
          class="question-nav-item"
          @click="scrollToQuestion(index)">
          Otázka {{ question.id }}
        </button>
      </nav>
    </aside>
    <main class="question-content">
      <div
        v-for="(question, index) in questions"
        :key="index"
        class="question-block"
        :ref="'question-' + index">
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
        <button class="download-pdf-button" @click="downloadPdf">Download PDF </button>
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
    navigateHome() {
      this.$router.push('/');
    },
    fetchQuestions() {
      const params = this.$route.query;
      const query = new URLSearchParams({
        numQuestions: params.numQuestions,
        startQuestion: params.startQuestion,
        endQuestion: params.endQuestion,
        numAnswers: params.numAnswers
      }).toString();
      const pocet_odpovedi = params.numAnswers

      //deployold fetch(`https://medik-cloud-i4zdozbjjq-lm.a.run.app/api/get_test_questions/?numQuestions=${params.numQuestions}&startQuestion=${params.startQuestion}&endQuestion=${params.endQuestion}`)
      //local fetch(`http://127.0.0.1:8081/api/get_test_questions/?numQuestions=${params.numQuestions}&startQuestion=${params.startQuestion}&endQuestion=${params.endQuestion}`)
      //          url: 'https://medik-cloud-deploy-xxtgwkr47a-uc.a.run.app/generate-pdf/',

      //fetch(`http://127.0.0.1:8081/api/get_test_questions/?${query}`)
      fetch(`https://medik-cloud-deploy-xxtgwkr47a-uc.a.run.app/api/get_test_questions/?${query}`)
        .then(response => response.json())
        .then(data => {
          this.questions = Object.entries(data).map(([key, value]) => ({
            ...value,
            id: key
          }));
          this.maxPoints = this.questions.length * pocet_odpovedi;
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
    },
    async downloadPdf() {
      try {
        // Create an array of questions with their answers in a format suitable for your backend
        const questionsData = this.questions.map(question => ({
          questionText: question.text,
          answers: question.answers.map(answer => ({
            answerText: answer[1], // assuming the text is the second element
            isCorrect: answer[2]  // assuming the correctness flag is the third element
          }))
        }));

        // Make a request to generate a PDF with this data
        const response = await this.$axios.post(
          'https://medik-cloud-deploy-xxtgwkr47a-uc.a.run.app/generate-pdf/',
          { questions: questionsData },
          { responseType: 'blob' }
        );

        // Create a Blob from the PDF binary data
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'test_questions.pdf');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error during PDF generation or download:', error);
      }
    },

    /*
    async generateTest() {
      try {
        const response = await this.$axios({
          //url: 'https://medik-cloud-i4zdozbjjq-lm.a.run.app/generate-pdf/', //deploy old
          //url: 'http://127.0.0.1:8081/generate-pdf/',                                        //localhost
          url: 'https://medik-cloud-deploy-xxtgwkr47a-uc.a.run.app/generate-pdf/',
          method: 'GET',
          responseType: 'blob',
          params: {
            numQuestions: this.numQuestions,
            startQuestion: this.startQuestion,
            endQuestion: this.endQuestion,
            numAnswers: this.numAnswers,
            categories: this.checkedCategories.join(',')
          },
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'tests_package.zip');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error during PDF generation or download:', error);
      }
    },
     */
    scrollToQuestion(index) {
      const questionRef = this.$refs['question-' + index][0];
      if (questionRef) {
        questionRef.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    },
  }
};

</script>

<style>

.home-button {
  padding: 10px;
  background: #7C4DFF;
  color: white;
}

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
  margin-right: 5px;
}

.submit-button:hover {
  background-color: #6841c9;
}


.download-pdf-button {
  padding: 10px 20px;
  background-color: #7C4DFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.download-pdf-button:hover {
  background-color: #6841c9;
}
</style>
