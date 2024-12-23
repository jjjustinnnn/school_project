const fs = require('fs');
const { initializeApp } = require("firebase/app");
const { getDatabase, ref, get, child } = require("firebase/database");
const { getAuth, signInWithEmailAndPassword } = require("firebase/auth");

// 取得從命令列傳入的 mac_address
const mac_address = process.argv[2];

// 打印 mac_address
console.log("Received MAC Address:", mac_address);

const firebaseConfig = {
    apiKey: "AIzaSyDzrGMkK5QYZe7l8CLFZwhfZ6J4avMk7I4",
    authDomain: "cmorecard-f8cc0.firebaseapp.com",
    databaseURL: "https://cmorecard-f8cc0-default-rtdb.firebaseio.com/",
    projectId: "cmorecard-f8cc0",
    storageBucket: "cmorecard-f8cc0.appspot.com",
    messagingSenderId: "485043221890",
    appId: "1:485043221890:web:7e3d30568f39b7f024cb9b",
    measurementId: "G-ET19TYZ0P7"
};

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);
signInWithEmailAndPassword(auth, "yzu_ee@tekpass.com.tw", "V@b0nox%W!u8lh%O%!f!2!Z$")
  .then((userCredential) => {
    // Signed in 
    const user = userCredential.user;
    console.log(userCredential.user.uid); // YRfJbvt1BuOszRSmGgKyg0Z4M873

    const db = getDatabase(app);
    const dbRef = ref(getDatabase());

    // 使用传递的 mac_address
    console.log(`Using MAC address: ${mac_address}`);

    get(child(dbRef, `/sso/${mac_address}:TPYZU`)).then((snapshot) => {
      if (snapshot.exists()) {
        const data = snapshot.val();
        console.log(data);

        // 保存 sso_id 到文件
        const sso_id = data.sso_id;
        console.log("sso_id:", sso_id);
        fs.writeFileSync('sso_id.txt', sso_id);

        // 保存 sso_token 到文件
        const sso_token = data.sso_token;
        console.log("sso_token:", sso_token);
        fs.writeFileSync('sso_token.txt', sso_token);
      } else {
        console.log('沒有資料');
      }
      // 成功后退出程序
      process.exit(0);
    }).catch((error) => {
      console.error(error);
      // 出错后退出程序
      process.exit(1);
    });
  })
  .catch((error) => {
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error(`Error: ${errorCode}, Message: ${errorMessage}`);
    // 登入失败后退出程序
    process.exit(1);
  });

