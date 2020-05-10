import React from "react";
import Field from './field.js';
import { Button, Message } from 'semantic-ui-react'
import axios from 'axios';
import { getUser, setUserSession } from './utils/common';
import './field.css';
import './index.css';

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      password: '',
      message: ''
    };
  }
  
  updatecredentials(field,value) {
    //console.log('parent:'+field + ':' + value);
    if(field === 'email'){
      this.setState({ email:value });
    }
    if(field === 'password'){
      this.setState({ password:value });
    }
  }

  authenticate(event){
    const { email, password, message } = this.state;
    this.setState({ message:'authenticating' });
    axios.post('http://127.0.0.1:8989/user/login', {},{
       auth: {
        username: email,
        password: password
      }
    })
    .then(response => { 
      if(response.status === 200){
        setUserSession(response.headers['access-token'],response.headers['name']);
        this.props.history.push('/home');
      }
    })
    .catch(error => {
      const errresponse = error.response
      if(errresponse){
        if(errresponse.status === 401){
          this.setState({ message:'incorrect username and/or password' });
        }
        else{
          this.setState({ message:errresponse });
        }
      }
      else{
        this.setState({ message:'internal server error' });
      }
    });
  }
  
  render() {
    const { email, password, message } = this.state;
    return (
      <div>
        <Field label="email" type="text" active={false}
        parentCallback={this.updatecredentials.bind(this)}/>
        <Field label="password" type="password" active={false}
        parentCallback ={this.updatecredentials.bind(this)}/>
        <Button secondary onClick={this.authenticate.bind(this)}>login</Button>
        <span className='error'>{message}</span>
      </div>
    )
  }
}
export default Login;
