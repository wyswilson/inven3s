import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken } from './utils/common';
import { Message, Divider, Input, Dropdown, Container, Grid, Button, Image } from 'semantic-ui-react'
import _ from 'lodash'

class Product extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://127.0.0.1:8989',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      actioned: false,
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      productsuggests: [],
      productdropdown: '',
      gtin: this.props.location.state.gtin || '',
      productname: this.props.location.state.productname || '',
      productimage: this.props.location.state.productimage || 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandname:  this.props.location.state.brandname || '',
      isedible:1,
      isperishable:0
    };
  }

  upsertproduct(event){
    this.setState({ actionedmsg: '' });
    this.setState({ actioned: false });
    this.setState({ loading: true });

    axios.post(this.state.apihost + '/product', 
      {
        gtin:this.state.gtin,
        productname:this.state.productname,
        productimage:this.state.productimage,
        brandname:this.state.brandname,
        isedible:this.state.isedible,
        isperishable:this.state.isperishable

      }, 
      {
        headers: {
          'crossDomain': true,
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => {
      this.setState({ loading: false });
      if(response.status === 200){
        this.setState({ inventory: response.data[0]['results'] });
        this.setState({ actionedmsg: response.data[0]['message'] });
        this.setState({ actioned: true });
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        this.setState({ actionedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('server unreachable');
        this.setState({ actionedmsg: 'server unreachable' });
      }
    });
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      axios.get(this.state.apihost + '/product/' + gtinorproduct + '?isedible=2',
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.updateproductsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  updateproductsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.gtin,
          text: item.productname,
          value: item.productname,
          img: item.productimage,
          brand: item.brandname
        }
      ));
    console.log(updatedsuggest);
    this.setState({ productsuggests: updatedsuggest });
  }

  setproductmetadata(event, data){
    const field = data.placeholder;
    const value = data.value;
    console.log(field + ':' + value);

    if(field === 'productdropdown'){
      const array = this.state.productsuggests;
      let selectedarr = array.filter(prod => prod.value.includes(value))[0];

      if(selectedarr){
        const selectedgtin = selectedarr['key'];
        const selectedimg = selectedarr['img'];
        const selectedbrand = selectedarr['brand'];

        this.setState({ productdropdown: value });
        this.setState({ gtin: selectedgtin });
        this.setState({ productname: value });
        this.setState({ productimage: selectedimg });
        this.setState({ brandname: selectedbrand });

        console.log(selectedgtin + ':' + value + ':' + selectedimg);
      }
      else{
        console.log('new product:' + value + ' => handled by addnewproduct')

      }
    }
  }

  addnewproduct(event,data){
    this.setState({ actionedmsg: '' });
    this.setState({ actioned: false });
    this.setState({ loading: true });

    const gtincandidate = data.value;
    console.log('onAddItem for product:' + gtincandidate);
    this.setState({ gtin: gtincandidate });
    
    axios.get(this.state.apihost + '/product/discover/' + gtincandidate,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        this.setState({ loading: false });
        if(response.status === 200){
          this.setState({ actionedmsg: response.data[0]['message'] });        
          this.setState({ actioned: true });

          const newproductdata = response.data[0]['results'][0]
          this.setState({ productdropdown: newproductdata['productname'] });
          this.setState({ gtin: newproductdata['gtin'] });
          this.setState({ productname: newproductdata['productname'] });
          this.setState({ productimage: newproductdata['productimage'] });
          this.setState({ brandname: newproductdata['brandname'] });
        }
      })
      .catch(error => {
        this.setState({ loading: false });
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
          this.setState({ actionedmsg: error.response.data[0]['message'] });        
        }
        else{
          console.log('server unreachable');
          this.setState({ actionedmsg: 'server unreachable' });        
        }
      });
  }

  productupsert(event){
    const { gtin, productname, productimage, brandname } = this.state;
    console.log(gtin + ':' + productname + ':' + productimage + ':' + brandname);
  }

  setdefaultimage(event){
    event.target.src = this.state.defaultimage;
  }

  generateitemadditionmsg(){
      if(this.state.actionedmsg !== '' && this.state.actioned){
        return (
          <Message className="fullwidth" success><Message.Header>{this.state.actionedmsg}</Message.Header></Message>
        )
      }
      else if(this.state.actionedmsg !== ''){
        return (
          <Message className="fullwidth" negative><Message.Header>{this.state.actionedmsg}</Message.Header></Message>        
        )
      }
  }

  componentDidMount() {
  }

  render() {
    return (
      <Container fluid>
        <Grid columns={1} doubling stackable>
          <Grid.Row columns={2}>
            <Grid.Column width={2}>
              <Image floated='left' size='tiny'
              src={this.state.productimage}
              onError={this.setdefaultimage.bind(this)}
              />
            </Grid.Column>
            <Grid.Column width={8}>
              <Dropdown className="fullwidth"
                placeholder="productdropdown"
                search
                selection
                allowAdditions
                value={this.state.productdropdown}
                options={this.state.productsuggests}
                additionLabel = "Add new product "
                onSearchChange={this.lookupproduct.bind(this)}
                onAddItem={this.addnewproduct.bind(this)}
                onChange={this.setproductmetadata.bind(this)}
              />
            </Grid.Column>
          </Grid.Row>
          <Divider />
          <Grid.Column>
            <Input placeholder='gtin' disabled value={this.state.gtin} className="fullwidth" />
          </Grid.Column>
          <Grid.Column>
            <Input placeholder='productname' value={this.state.productname} className="fullwidth" onChange={e => this.setState({ productname: e.target.value })}/>
          </Grid.Column>
          <Grid.Column>
            <Input placeholder='productimage' value={this.state.productimage} className="fullwidth" onChange={e => this.setState({ productimage: e.target.value })}/>                     
          </Grid.Column>
          <Grid.Column>
            <Input placeholder='brandname' value={this.state.brandname} className="fullwidth" onChange={e => this.setState({ brandname: e.target.value })}/>                     
          </Grid.Column>
          <Grid.Row columns={2}>
            <Grid.Column>
              
            </Grid.Column>
            <Grid.Column>
                      
            </Grid.Column>
          </Grid.Row>
          <Divider />
          <Grid.Row columns={2}>
            <Grid.Column>
              <Button loading={this.state.loading || false} className="fullwidth" color='black' onClick={this.upsertproduct.bind(this)}>
                add
              </Button>
            </Grid.Column>
            <Grid.Column>
              {this.generateitemadditionmsg()}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    )
  }
}
export default Product;

