// app.js
import React, { Component } from 'react';
import './App.css';
import MainForm from './components/MainForm';
import { Container } from 'semantic-ui-react';
import SideBar from "./sidebar";

class App extends Component {

  render() {
    return(
      <Container textAlign='center'>
        <SideBar pageWrapId={"page-wrap"} outerContainerId={"App"} />
        <MainForm />
      </Container>     )
  }
}

export default App;