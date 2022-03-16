import Feedback from './Feedback.svelte';

try {
	var app = new Feedback({ target: document.querySelector('#feedbackform')});
} catch (error) { 
	var app = null; 
}

export default app;
