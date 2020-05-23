import React from "react";
import axios from 'axios';
import { getToken } from './utils/common';
import { Checkbox, Card, Label, Message, Divider, Input, Dropdown, Grid, Button, Image } from 'semantic-ui-react'
import _ from 'lodash'
//import queryString from 'query-string'

class Product extends React.Component {
  constructor(props) {
    super(props)
    const redirectstate = this.props.location.state;
    //const querystr = queryString.parse(this.props.location.search);
    this.state = {
      apihost: 'http://13.229.67.229:8989',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      actioned: false,
      //queryisedible: querystr ? querystr.isedible : '2',
      //queryisopened: querystr ? querystr.isopened : '2',
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      productsuggests: [],
      brandsuggests: [],
      productdropdown: '',
      gtin: redirectstate ? redirectstate.gtin : '',
      productname: redirectstate ? redirectstate.productname : '',
      productimage: redirectstate ? redirectstate.productimage : 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandname: redirectstate ? redirectstate.brandname : '',
      isedible: redirectstate ? redirectstate.isedible : 1,
      isperishable:0
    };
  }

  upsertproduct(event){
    this.setState({ actionedmsg: '' });
    this.setState({ actioned: false });
    this.setState({ loading: true });

    console.log('upsertproduct');

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
        console.log('upsertproduct [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });
        this.setState({ actioned: true });

        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        console.log('upsertproduct [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        this.setState({ actionedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('upsertproduct [server unreachable]');
        this.setState({ actionedmsg: 'server unreachable' });
      }
    });
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      this.searchproducts(gtinorproduct);
    }
  }

  searchproducts(gtinorproduct){
    console.log('searchproducts [' + gtinorproduct + ']');

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
          console.log('searchproducts [' + response.data[0]['message'] + ']');
          
          this.updateproductsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('searchproducts [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        }
        else{
          console.log('searchproducts [server unreachable]');
        }
      });
  }

  updateproductsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.gtin,
          text: item.productname,
          value: item.productname,
          img: item.productimage,
          brand: item.brandname,
          isedible: item.isedible
        }
      ));
    console.log(updatedsuggest);
    this.setState({ productsuggests: updatedsuggest });
  }

  setproductmetadata(event, data){
    const field = data.name;
    const value = data.value;
    console.log('setproductmetadata [' + field + ':' + value + ']');

    if(field === 'productname'){
      const array = this.state.productsuggests;
      let selectedarr = array.filter(prod => prod.value.includes(value))[0];

      if(selectedarr){
        const selectedgtin = selectedarr['key'];
        const selectedimg = selectedarr['img'];
        const selectedbrand = selectedarr['brand'];
        const selectedisedible = selectedarr['isedible'];

        this.setState({ productdropdown: value });
        this.setState({ gtin: selectedgtin });
        this.setState({ productname: value });
        this.setState({ productimage: selectedimg });
        this.setState({ brandname: selectedbrand });
        this.setState({ isedible: selectedisedible });
        
        this.searchbrands(selectedbrand);
      }
      else{
        //NEW PRODUCT
      }
    }
    else if(field === 'brandname'){
      const array = this.state.brandsuggests;
      let selectedarr = array.filter(brand => brand.value.includes(value))[0];
      if(selectedarr){
        const brandid = selectedarr['key'];

        this.setState({ brandid: brandid });
        this.setState({ brandname: value });
      }
      else{
        //NEW BRAND
      }
    }
  }

  addnewbrand(event,data){
    this.setState({ actionedmsg: '' });
    this.setState({ actioned: false });
    this.setState({ loading: true });

    const newbrand = data.value;
    console.log('addnewbrand [' + newbrand + ']');

    axios.post(this.state.apihost + '/brand', 
      {
        brandid:'',
        brandname:newbrand,
        brandimage:'',
        brandurl:'',
        brandowner:''
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
        console.log('addnewbrand [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });        
        this.setState({ actioned: true });

        this.setState({ brandid: response.data[0]['results'][0]['brandid'] });
        this.setState({ brandname: response.data[0]['results'][0]['brandname'] });
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        console.log('addnewbrand [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        this.setState({ actionedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('addnewbrand [server unreachable]');
        this.setState({ actionedmsg: 'server unreachable' });        
      }
    });    
  }

  addnewproduct(event,data){
    this.setState({ actionedmsg: '' });
    this.setState({ actioned: false });
    this.setState({ loading: true });

    const gtincandidate = data.value;
    console.log('addnewproduct [' + gtincandidate + ']');
    
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
          console.log('addnewproduct [' + response.data[0]['message'] + ']');
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
          console.log('addnewproduct [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          this.setState({ actionedmsg: error.response.data[0]['message'] });        
        }
        else{
          console.log('addnewproduct [server unreachable]');
          this.setState({ actionedmsg: 'server unreachable' });        
        }
      });
  }

  updatebrandsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.brandid,
          text: item.brandname,
          value: item.brandname,
        }
      ));
    this.setState({ brandsuggests: updatedsuggest });
  }  

  lookupbrand(event, data){
    const brand = data.searchQuery;

    if(brand.length > 1){
      this.searchbrands(brand);
    }
  }

  searchbrands(brand){
    console.log('searchbrands [' + brand + ']');

    axios.get(this.state.apihost + '/brand/' + brand,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          console.log('searchbrands [' + response.data[0]['message'] + ']');
          this.updatebrandsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('searchbrands [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        }
        else{
          console.log('searchbrands [server unreachable]');
        }
      });
  }

  setdefaultimage(event){
    event.target.src = this.state.defaultimage;
  }

  updateedibletoggle(event,data){
    if(data.checked){
      this.setState({ isedible: 1 });
    }
    else{
      this.setState({ isedible: 0 });
    }
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
    //ONLOAD, IF REDIRECT WITH PRODUCT DETAILS FROM INVENTORY. NEED TO POPULATE DROPDOWN
    if(this.state.brandname !== ''){
      this.searchbrands(this.state.brandname);
    }
   
  }

  checktoggle(){
    if(this.state.isedible === 1){
      return true;
    }
    else{
      return false;
    }
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
                <Dropdown className="fullwidth" name="productname" 
                    placeholder="Oreo Cookie Original 133G"
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
              </Grid.Column>
            </Grid>
          </Card.Description>
          <Divider/>
          <Card.Meta>
            <Grid columns={1} doubling stackable>
              <Grid.Column>
                <label className="fullwidth">GTIN</label>
                <Input className="fullwidth" disabled value={this.state.gtin}/>
              </Grid.Column>
              <Grid.Column>
                <label className="fullwidth">Product</label>
                <Input placeholder='Oreo Cookie Original 133G' value={this.state.productname} className="fullwidth" onChange={e => this.setState({ productname: e.target.value })}/>
              </Grid.Column>
              <Grid.Column>
                <label className="fullwidth">Image</label>
                <Input placeholder='Product image' value={this.state.productimage} className="fullwidth" onChange={e => this.setState({ productimage: e.target.value })}/>                     
              </Grid.Column>
              <Grid.Column>
                <label className="fullwidth">Brand</label>
                <Dropdown className="fullwidth" name="brandname" 
                  placeholder="Oreo"
                  search
                  selection
                  allowAdditions
                  value={this.state.brandname}
                  options={this.state.brandsuggests}
                  additionLabel = "Add new brand "
                  noResultsMessage = "No brand found"
                  onSearchChange={this.lookupbrand.bind(this)}
                  onAddItem={this.addnewbrand.bind(this)}
                  onChange={this.setproductmetadata.bind(this)}
                />
              </Grid.Column>
              <Grid.Row columns={2}>
                <Grid.Column>
                   <Checkbox toggle label='Is edible?' checked={this.checktoggle()} onChange={this.updateedibletoggle.bind(this)}/>
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
              <Button loading={this.state.loading || false} className="fullwidth" color='grey' onClick={this.upsertproduct.bind(this)}>
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

