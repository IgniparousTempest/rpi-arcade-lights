#include <libconfig.h>
#include <stdbool.h>
#include <stdlib.h>
#include <syslog.h>
#include <string.h>

typedef struct Game {
    const char* name;
    bool buttons[8];
    struct Game* next;
} Game_t;

typedef struct Config {
    int button_count;
    Game_t* games;
} Config_t;

/// Constructs an empty config file.
/// \return Blank config
Config_t _empty_config() {
    Config_t config;
    config.button_count = 0;
    config.games = NULL;
    return config;
}

/// Reads the config file from /usr/share/rpifan/config.cfg
/// \return The config
struct Config read_config() {
    Config_t config;
    struct Game* current_game = NULL;
    config_t cfg;
    config_setting_t *setting;
    int qty;

    openlog("rpi-arcade-lights", LOG_ODELAY, LOG_USER);

    config_init(&cfg);

    // Load default if config file is missing
//    if(!config_read_file(&cfg, "/usr/share/rpi-arcade-lights/config.cfg"))
    if(!config_read_file(&cfg, "/home/courts/rpi-arcade-lights/config.cfg"))
    {
        syslog(LOG_WARNING, "Config file could not be opened, using defaults for all values.");
        return _empty_config();
    }

    // Read the number of buttons on the machine
    if(config_lookup_int(&cfg, "num_of_buttons", &qty))
        config.button_count = qty;
    else {
        syslog(LOG_WARNING, "Config file is missing temp_threshold, using default.");
        return _empty_config();
    }

    // Read games list
    setting = config_lookup(&cfg, "games");
    if(setting != NULL)
    {
        int count = config_setting_length(setting);

        for(unsigned int i = 0; i < count; ++i)
        {
            config_setting_t *game_setting = config_setting_get_elem(setting, i);

            // Only output the record if all of the expected fields are present.
            const char *name, *buttons;

            if(!(config_setting_lookup_string(game_setting, "name", &name)
                 && config_setting_lookup_string(game_setting, "buttons", &buttons)))
                continue;

            // Create game entry
            Game_t* game = malloc(sizeof(Game_t));
            game->name = name;
            for (int j = 0; j < 8; ++j) {
                char str[2];
                sprintf(str, "%d", j + 1);
                if(strstr(buttons, str) != NULL)
                    game->buttons[j] = true;
                else
                    game->buttons[j] = false;
            }
            game->next = NULL;

            // Append game entry
            if (current_game == NULL) {
                config.games = game;
                current_game = config.games;
            } else {
                current_game->next = game;
                current_game = current_game->next;
            }
        }
    }

    closelog();
    return config;
}

/// Triggers the leds
/// \param config
/// \param pattern
void turn_on_leds(Config_t config, bool pattern[8]) {
    printf("buttons:");
    if (config.button_count >= 1)
        printf(" %d", pattern[0]);

    if (config.button_count >= 2)
        printf(" %d", pattern[1]);

    if (config.button_count >= 3)
        printf(" %d", pattern[2]);

    if (config.button_count >= 4)
        printf(" %d", pattern[3]);

    if (config.button_count >= 5)
        printf(" %d", pattern[4]);

    if (config.button_count >= 6)
        printf(" %d", pattern[5]);

    if (config.button_count >= 7)
        printf(" %d", pattern[6]);

    if (config.button_count >= 8)
        printf(" %d", pattern[7]);

    printf("\n");
}

/// Lights the buttons corresponding for the current game, lights all the buttons if there was no config for the current game.
/// \param config The current config.
/// \param game_name The name of the game.
void light_buttons(Config_t config, const char* game_name) {
    Game_t* curr = config.games;
    while (curr != NULL) {
        // Found Game
        if (strcmp(curr->name, game_name) == 0) {
            turn_on_leds(config, curr->buttons);
            return;
        }
        curr = curr->next;
    }

    // Did not find game
    syslog(LOG_WARNING, "Game was not found, lighting all buttons.");
    bool all_on[] = {true, true, true, true, true, true, true, true};
    turn_on_leds(config, all_on);
    printf("unknown game : 1 1 1 1 1 1 1 1\n");
}

/// Prints the help screen.
/// \param program_name The name the user typed to execute the program.
/// \param config The current config.
void print_help(const char* program_name) {
    printf("Usage: %s [-h] GAME_NAME\n", program_name);
    printf("Controls the LEDs of the arcade buttons.\n");
    printf("\n");
    printf("  -h, --help        displays this help screen.\n");
}

int main(int argc, char *argv[]) {
    // Show help
    if (argc == 2 && (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0))
        print_help(argv[0]);
    // Light buttons for specified game
    else if (argc == 2) {
        Config_t config = read_config();
        light_buttons(config, argv[1]);
    }
    // Show error screen
    else {
        printf("%s: invalid input '%s'\n", argv[0], argv[1]);
        printf("Try '%s --help' for more information.\n", argv[0]);
    }
    return 0;
}