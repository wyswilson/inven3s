import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken } from './utils/common';
import { Card, Label, Message, Divider, Input, Dropdown, Container, Grid, Button, Image } from 'semantic-ui-react'
import _ from 'lodash'

class Product extends React.Component {
  constructor(props) {
    super(props)
    const redirectstate = this.props.location.state;
    this.state = {
      apihost: 'http://127.0.0.1:8989',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      actioned: false,
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      productsuggests: [],
      productdropdown: '',
      gtin: redirectstate ? redirectstate.gtin : '',
      productname: redirectstate ? redirectstate.productname : '',
      productimage: redirectstate ? redirectstate.productimage : 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandname: redirectstate ? redirectstate.brandname : '',
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

    if(field === 'Product name or GTIN'){
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
      <Card raised fluid>
        <Card.Content>
          <Card.Description>
            <Grid columns={1} doubling stackable>
              <Grid.Column>
                 <Image rounded
                centered src={this.state.productimage}
                floated='right'
                size='tiny' style={{width: 'auto', height: '140px'}}
                onError={this.setdefaultimage.bind(this)}
              />
              <Dropdown className="halfwidth"
                  placeholder="Product name or GTIN"
                  search
                  selection
                  allowAdditions
                  value={this.state.productdropdown}
                  options={this.state.productsuggests}
                  additionLabel = "Add new product "
                  noResultsMessage = "No product found"
                  onSearchChange={this.lookupproduct.bind(this)}
                  onAddItem={this.addnewproduct.bind(this)}
                  onChange={this.setproductmetadata.bind(this)}
                />
                <Input placeholder='GTIN' className="halfwidth" disabled value={this.state.gtin}/>
              </Grid.Column>
            </Grid>
          </Card.Description>
          <Divider/>
          <Card.Meta>
            <Grid columns={1} doubling stackable>
              <Grid.Column>
                <Input placeholder='Product name' value={this.state.productname} className="fullwidth" onChange={e => this.setState({ productname: e.target.value })}/>
              </Grid.Column>
              <Grid.Column>
                <Input placeholder='Product image' value={this.state.productimage} className="fullwidth" onChange={e => this.setState({ productimage: e.target.value })}/>                     
              </Grid.Column>
              <Grid.Column>
                <Input placeholder='Brand' value={this.state.brandname} className="fullwidth" onChange={e => this.setState({ brandname: e.target.value })}/>                     
              </Grid.Column>
              <Grid.Row columns={2}>
                <Grid.Column>
                  
                </Grid.Column>
                <Grid.Column>
                          
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Card.Meta>
          <Label color='grey' attached='top right'>0</Label>
        </Card.Content>
        <Card.Content extra textAlign="center">
          <Grid columns={2} doubling stackable>
            <Grid.Column>
              <Button loading={this.state.loading || false} className="fullwidth" color='black' onClick={this.upsertproduct.bind(this)}>
                Add or update
              </Button>
            </Grid.Column>
            <Grid.Column>
              {this.generateitemadditionmsg()}
            </Grid.Column>
          </Grid>
        </Card.Content>
      </Card>

    )
  }
}
export default Product;

