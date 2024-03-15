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
    <button @click="generateTest">Generate and Download Test</button>
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
    generateTest() {
      // Placeholder content generation logic
      const testContent = `Test generated with ${this.numQuestions} questions from question ID ${this.startQuestion} to ${this.endQuestion}.`;

      // Download logic
      const element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(testContent));
      element.setAttribute('download', 'test.txt');

      element.style.display = 'none';
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
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
