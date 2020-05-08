import React from "react";
import Field from './field.js';
import './field.css';
import { Button } from 'semantic-ui-react'
import axios from 'axios';
import { setUserSession } from './utils/common';

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      password: ''
    };
  }
  
  updatecredentials(field,value) {
    console.log('parent:'+field + ':' + value);
    if(field === 'email'){
      this.setState({ email:value });
    }
    if(field === 'password'){
      this.setState({ password:value });
    }
  }

  authenticate(event){
    const { email, password } = this.state;
    console.log('authenticating... with [' + email + ':' + password + ']');  
    axios.post('http://127.0.0.1:8989/user/login', {},{
       auth: {
        username: email,
        password: password
      }
    })
    .then(response => { 
      if(response.status === 200){
        setUserSession(response.headers['access-token'],response.headers['identifier']);
        //props.history.push('/insights');
        console.log('successful! ' + response.headers['access-token']);
      }
    })
    .catch(error => {
      const err_response = error.response
      if(err_response){
        if(err_response.status === 401){
          console.log("login failed");
        }
        else{
          console.log(err_response);
        }
      }
      else{
        console.log('internal server error');
      }
    });
  }
  
  render() {
    return (
      <div>
        <Field label="email" type="text" active={false}
        parentCallback={this.updatecredentials.bind(this)}/>
        <Field label="password" type="password" active={false}
        parentCallback ={this.updatecredentials.bind(this)}/>
        <Button onClick={this.authenticate.bind(this)}>login</Button>
      </div>
    )
  }
}
export default Login;
