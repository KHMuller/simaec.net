import firebase from 'firebase/compat/app';
import "firebase/compat/firestore"

const config = {
    apiKey: "replace-with-your-value",
    authDomain: "replace-with-your-value",
    projectId: "replace-with-your-value",
    storageBucket: "replace-with-your-value",
    messagingSenderId: "replace-with-your-value",
    appId: "replace-with-your-value"
}

if (!firebase.apps.length) {
  firebase.initializeApp(config)
}

const firestore = firebase.firestore()

export { firestore }
