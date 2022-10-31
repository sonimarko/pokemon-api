from odoo import api, models, api, exceptions, fields, _
from odoo.exceptions import UserError
import base64
import requests

url = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon(models.Model):
	_name = 'ns.pokemon'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = 'Pokemon'

	name = fields.Char(string='Name')
	type = fields.Char(string='Type')
	image = fields.Binary(string='Image')
	move_ids = fields.One2many('ns.pokemon.move', 'pokemon_id', string='Pokemon Move')
	ns_ability_ids = fields.One2many('ns.pokemon.move', 'pokemon_id', string='Pokemon Ability')

class PokemonMove(models.Model):
	_name = 'ns.pokemon.move'
	_description = 'Pokemon Move'

	name = fields.Char()
	pokemon_id = fields.Many2one('ns.pokemon', string='Pokemon')

class PokemonWizard(models.TransientModel):
	_name = 'ns.pokemon.wizard'
	_description = 'Pokemon Wizard'

	name = fields.Char()

	def add_pokemon(self):
		url_name = url + str.lower(self.name)

		pokemon_name = self.name.capitalize()
		pokemon_type = False
		pokemon_moves = []
		pokemon_abilities = []
		pokemon_image = False

		response = requests.get(url_name)

		if response.status_code != 200: 
			raise UserError("Pokemon Not Found")
		else:
			pokemon_obj = self.env['ns.pokemon']
			
			data = response.json()

			# Type
			pokemon_type = data['types'][0]['type']['name'].capitalize()

			# Moves
			for move in data['moves']:
				pokemon_moves.append((0,0,{'name':move['move']['name']}))

			# Abilities
			for ability in data['abilities']:
				pokemon_abilities.append((0,0,{'name':ability['ability']['name']}))

			# Image
			image_url = data['sprites']['front_default']
			pokemon_image = base64.b64encode(requests.get(image_url.strip()).content).replace(b'\n', b'')

			new_pokemon = pokemon_obj.create({
				'name': pokemon_name,
				'type': pokemon_type,
				'image': pokemon_image,
				'move_ids': pokemon_moves,
				'ns_ability_ids': pokemon_abilities,
			})

			# Attachment
			attachment_images = []

			if data['sprites']['back_default']:
				attachment_images.append(data['sprites']['back_default'])
			if data['sprites']['back_female']:
				attachment_images.append(data['sprites']['back_female'])
			if data['sprites']['back_shiny']:
				attachment_images.append(data['sprites']['back_shiny'])
			if data['sprites']['back_shiny_female']:
				attachment_images.append(data['sprites']['back_shiny_female'])
			if data['sprites']['front_default']:
				attachment_images.append(data['sprites']['front_default'])
			if data['sprites']['front_female']:
				attachment_images.append(data['sprites']['front_female'])
			if data['sprites']['front_shiny']:
				attachment_images.append(data['sprites']['front_shiny'])
			if data['sprites']['front_shiny_female']:
				attachment_images.append(data['sprites']['front_shiny_female'])

			count = 0
			for image in attachment_images:
				count += 1
				title = 'Image #' + str(count)
				base64_image = base64.b64encode(requests.get(image.strip()).content).replace(b'\n', b'')
				attachment = self.env['ir.attachment'].create({
					'name': title,
					'type': 'binary',
					'datas': base64_image,
					'res_model': 'ns.pokemon',
					'res_id': new_pokemon.id,
				})
			

class PokemonAbility(models.Model):
	_name = 'ns.ability'
	_description = 'Pokemon Ability'

	name = fields.Char()
	pokemon_id = fields.Many2one('ns.pokemon', string='Pokemon')