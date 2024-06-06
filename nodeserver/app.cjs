var ini = require('ini')
var fs = require('fs')
const { initializeApp, applicationDefault, cert } = require('firebase-admin/app');
const { getFirestore, Timestamp, FieldValue, Filter } = require('firebase-admin/firestore');
var config = ini.parse(fs.readFileSync('../app/data/configfile.ini', 'utf-8'))

const serviceAccount = require('./serviceAccountKey.json');

initializeApp({
  credential: cert(serviceAccount)
});
const db = getFirestore();

// const settingsdata = {
// irrigation_interval: 10,
// irrigation_area: 10,
// irrigation_amount: 5,
// auto_irrigation: 'yes',
// irrigation_threshold: 50,
// data_check_interval: 24,
// };

// const weathersettingsdata = {
//   api_key: 'be2cd6aacc1d683d9e90307476bde268',
//   lat: '36.35',
//   lon: '43.16',
//   };
// const res = db.collection('irrigation').doc('settings').set(settingsdata);
// const res1 = db.collection('irrigation').doc('weathersettings').set(weathersettingsdata);


const doc = db.collection('irrigation');
const observer = doc.onSnapshot(querySnapshot => {
    querySnapshot.docChanges().forEach(change => {
      if (change.type === 'modified') {
          config[change.doc.id] = change.doc.data();
          text = ini.stringify(config);
          fs.writeFileSync('../app/data/configfile.ini',text,)
          var datetime = new Date();
          console.log(datetime, change.doc.id, 'changed successfuly')
      }
    });
  });
