// Selectors for elements
const startQuizBtnEl = document.getElementById("start-quiz-btn-el");
const quizContainerEl = document.getElementById('quiz-container-el');
const quizAnswerContainerEl = document.getElementById('quiz-answer-container-el');
const nextQuestionBtnEl = document.getElementById('next-question-btn-el');
const reviewContainerEl = document.getElementById('review-container-el');
const reviewContentEl = document.getElementById('review-content-el');
const backToQuizBtnEl = document.getElementById('back-to-quiz-btn-el');


let currentQuestionIndex = 0;
let questions = [];
let score = 0;
let moneyEarned = 0;
let userAnswers = [];
let cash = 0; // Initialize cash

// Event listeners
startQuizBtnEl.addEventListener("click", (e) => {
  e.preventDefault();
  renderLoadingAnimation();
  fetch("/quiz/get-questions")
    .then((res) => res.json())
    .then((data) => {
      quizContainerEl.innerHTML = '';
      questions = data.questions;
      currentQuestionIndex = 0;
      userAnswers = [];
      startQuiz();
    })
    .catch(error => console.error('Error fetching questions:', error));
});

nextQuestionBtnEl.addEventListener("click", (e) => {
  e.preventDefault();
  currentQuestionIndex++;
  renderQuizQuestion();
  quizAnswerContainerEl.innerHTML = ''; // Clear previous answer result
  nextQuestionBtnEl.classList.add('hidden');
});

backToQuizBtnEl.addEventListener("click", (e) => {
  e.preventDefault();
  reviewContainerEl.classList.add('hidden');
  quizContainerEl.classList.remove('hidden');
  location.reload();
});

// Functions
function startQuiz() {
  renderQuizQuestion();
}

function renderQuizQuestion() {
  if (currentQuestionIndex < questions.length) {
    const question = questions[currentQuestionIndex];
    const questionText = question.question;
    const optionA = question.option_a;
    const optionB = question.option_b;
    const optionC = question.option_c;
    const correctAnswer = question.answer;

    quizContainerEl.innerHTML = `
      <div class="quiz-content">
        <h2>Question ${currentQuestionIndex + 1}</h2>
        <p>${questionText}</p>
        <button class='btn-primary btn mt-4 mb-2 btn-block' id="optionA-btn">${optionA}</button>
        <button class='btn-primary btn mt-4 mb-2 btn-block' id="optionB-btn">${optionB}</button>
        <button class='btn-primary btn mt-4 mb-2 btn-block' id="optionC-btn">${optionC}</button>
      </div>
    `;

    document.getElementById('optionA-btn').addEventListener('click', () => checkUserAnswer(optionA, correctAnswer));
    document.getElementById('optionB-btn').addEventListener('click', () => checkUserAnswer(optionB, correctAnswer));
    document.getElementById('optionC-btn').addEventListener('click', () => checkUserAnswer(optionC, correctAnswer));
  } else {
    showReviewSection();
  }
}

function checkUserAnswer(userSelection, correctAnswer) {
  const buttons = document.querySelectorAll('.quiz-content button');
  buttons.forEach(button => {
    button.disabled = true;
    button.classList.add('disabled');
  });

  let isCorrect = userSelection === correctAnswer;

  if (isCorrect) {
    score++;
    moneyEarned += 5;
  }

  userAnswers.push({
    question: questions[currentQuestionIndex],
    userSelection,
    correctAnswer,
    isCorrect,
    explanation: ""
  });

  getAnswerExplanation(
    questions[currentQuestionIndex].question,
    userSelection,
    correctAnswer,
    questions[currentQuestionIndex].option_a,
    questions[currentQuestionIndex].option_b,
    questions[currentQuestionIndex].option_c,
    (explanation) => {
      userAnswers[currentQuestionIndex].explanation = explanation;
      renderQuestionResult(userSelection, correctAnswer, isCorrect);
    }
  );
}

function renderQuestionResult(userSelection, correctAnswer, isCorrect) {
  nextQuestionBtnEl.classList.remove('hidden');

  if (isCorrect) {
    incrementUserCash();
    quizAnswerContainerEl.innerHTML = `
      <h3 class='mt-2 mb-2'>Hooray! Correct!</h3>
      <h5 class='mt-2 mb-2'>Your answer: ${userSelection}</h5>
      <h5 class='mt-2 mb-2'>Correct answer: ${correctAnswer}</h5>
      <p>You Earned RM5! Keep it up!</p>
    `;
  } else {
    quizAnswerContainerEl.innerHTML = `
      <h3 class='mt-2 mb-2'>Oh darn! Wrong Answer.</h3>
      <h5 class='mt-2 mb-2'>Your answer: ${userSelection}</h5>
      <h5 class='mt-2 mb-2'>Correct answer: ${correctAnswer}</h5>
      <p>Better luck next time!</p>
    `;
  }
}

function getAnswerExplanation(question, userAnswer, correctAnswer, optionA, optionB, optionC, callback) {
  fetch('/quiz/generate-explanation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question: question,
      user_answer: userAnswer,
      correct_answer: correctAnswer,
      option_a: optionA,
      option_b: optionB,
      option_c: optionC
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log(data);
    callback(data.explanation);
  })
  .catch(error => console.error('Error fetching explanation:', error));
}

function showReviewSection() {
  quizContainerEl.classList.add('hidden');
  reviewContainerEl.classList.remove('hidden');
  reviewContentEl.innerHTML = '';

  userAnswers.forEach((answer, index) => {
    reviewContentEl.innerHTML += `
      <div class="review-item">
        <h4>Question ${index + 1}</h4>
        <p>${answer.question.question}</p>
        <p>Your answer: ${answer.userSelection}</p>
        <p>Correct answer: ${answer.correctAnswer}</p>
        <p>${answer.isCorrect ? 'Correct' : 'Wrong'}</p>
        <p>Explanation: ${answer.explanation}</p>
      </div>
    `;
  });
}

function incrementUserCash() {
  fetch('/quiz/increment-cash')
    .then(res => res.json())
    .then(data => {
      updateCash(data.new_cash);
    })
    .catch(err => console.error('Error incrementing cash:', err));
}

function renderLoadingAnimation() {
  quizContainerEl.innerHTML = '<div class="loader"></div>';
}

function updateCash(newCashAmount) {
  cash = newCashAmount;
  renderCash();
}

function renderCash() {
  const cashAmountEl = document.getElementById('cash-amount');
  if (cashAmountEl) {
    cashAmountEl.textContent = cash.toFixed(2);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const cashAmountEl = document.getElementById('cash-amount');
  cash = parseFloat(cashAmountEl.getAttribute('data-cash'));

  renderCash();
});
