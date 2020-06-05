import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken } from './utils/common';
import { Checkbox, Card, Label, Message, Divider, Input, Dropdown, Grid, Button, Image } from 'semantic-ui-react'
import _ from 'lodash'


class List extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      actioned: false
    };
  }


  

  componentDidMount() {

   
  }
  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
      </div>
    )
  }
}
export default Product;

