import App from './App.svelte';

try {
	var app = new App({ target: document.querySelector('#subscriptionform') });
} catch (error) { 
	var app = null; 
}

export default app;
