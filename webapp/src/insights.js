import React from "react";
import Field from './field.js';
import { Button, Message } from 'semantic-ui-react'
import axios from 'axios';
import { getUser, setUserSession } from './utils/common';
import './field.css';
import './index.css';

class Insights extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      username: getUser()
    };
  }
  
  handleChange(e) {
    e.preventDefault()
  }
  
  render() {
  	const { username } = this.state;

    return (
     <div>
      Insights for {username}!<br /><br />
      
      Bla bla
    </div>
    )
  }
}
export default Insights;

