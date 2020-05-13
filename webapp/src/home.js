import React from "react";
import './index.css';
import { Container, Button } from 'semantic-ui-react'
import { getUser, removeUserSession } from './utils/common';


class Insights extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      username: getUser()
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  handleChange(e) {
    e.preventDefault()
  }
  
  render() {
  	const { username } = this.state;

    return (
      <Container fluid>
        Insights for {username}!<br /><br />
        
        <Button color="black" onClick={this.handlelogout.bind(this)}>logout</Button>
      </Container>
    )
  }
}
export default Insights;

