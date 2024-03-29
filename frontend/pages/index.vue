<template>
  <div class="container">
    <h1>Generate and Download Test</h1>
    <div>
      <label for="numQuestions">Number of Questions:</label>
      <input type="number" id="numQuestions" v-model.number="numQuestions" min="1" />
    </div>
    <div>
      <label for="startQuestion">From Question ID:</label>
      <input type="number" id="startQuestion" v-model.number="startQuestion" min="1" />
    </div>
    <div>
      <label for="endQuestion">To Question ID:</label>
      <input type="number" id="endQuestion" v-model.number="endQuestion" min="1" />
    </div>
    <button @click="generateTest">Download Test</button>
    <button @click="generateInteractiveTest">Generate Interactive Test</button>

  </div>
</template>

<script>
export default {
  data() {
    return {
      numQuestions: 5,
      startQuestion: 1,
      endQuestion: 10,
    };
  },
  methods: {
    async generateTest() {
      try {
        const response = await this.$axios({
          url: 'https://medik-cloud-i4zdozbjjq-lm.a.run.app/generate-pdf/',
          method: 'GET',
          responseType: 'blob',
          params: {
            numQuestions: this.numQuestions,
            startQuestion: this.startQuestion,
            endQuestion: this.endQuestion,
          },
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        // Update the filename to indicate it's a ZIP file
        link.setAttribute('download', 'tests_package.zip');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error during PDF generation or download:', error);
      }
    },
    generateInteractiveTest() {
      // Navigate using the path
      this.$router.push({
        path: '/interaktivny_test', // Use the correct path
        query: {
          numQuestions: this.numQuestions.toString(),
          startQuestion: this.startQuestion.toString(),
          endQuestion: this.endQuestion.toString(),
        }
      });
    },
  },

};
</script>

<style>
.container {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}
div {
  margin-bottom: 20px;
}
</style>
